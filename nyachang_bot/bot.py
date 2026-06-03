"""Telegram application entry point."""

from __future__ import annotations

import html
import logging
import os
from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from nyachang_bot.config import BotConfig, load_config
from nyachang_bot.content import ContentError, ContentRepository, GuideNode, MediaAsset


logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

CALLBACK_HOME = "home"
CALLBACK_OPEN_PREFIX = "open:"
CALLBACK_ADMIN_PREFIX = "admin:"
MAX_MESSAGE_LENGTH = 3900


def build_application(config: BotConfig) -> Application:
    repository = ContentRepository(config.content_file)
    repository.reload()

    application = Application.builder().token(config.bot_token).build()
    application.bot_data["config"] = config
    application.bot_data["content"] = repository

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("reload_content", reload_content_command))
    application.add_handler(CommandHandler("content_ids", content_ids_command))
    application.add_handler(CommandHandler("settext", settext_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    application.add_handler(CallbackQueryHandler(callback_router))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_text_message))
    application.add_error_handler(error_handler)
    return application


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    repository = get_repository(context)
    await send_or_edit(
        update,
        context,
        format_home_text(repository),
        guide_keyboard(repository.root_nodes()),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "<b>Как пользоваться ботом</b>\n\n"
        "Нажимайте кнопки, чтобы открыть разделы гида по переезду и жизни в Нячанге. "
        "Если у раздела есть фото или видео, бот отправит их после текста.\n\n"
        "Команды:\n"
        "/start - открыть главное меню\n"
        "/help - показать подсказку\n"
        "/cancel - отменить текущее действие"
    )
    if is_admin(update, context):
        text += (
            "\n\n<b>Команды владельца</b>\n"
            "/admin - панель редактирования\n"
            "/reload_content - перечитать content/guide.json\n"
            "/content_ids - показать ID разделов\n"
            "/settext ID и далее с новой строки текст - быстро заменить текст раздела"
        )
    await require_message(update).reply_text(text, parse_mode=ParseMode.HTML)


async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or query.data is None:
        return
    await query.answer()

    data = query.data
    if data == CALLBACK_HOME:
        await show_home(update, context)
    elif data.startswith(CALLBACK_OPEN_PREFIX):
        await show_node(update, context, data.removeprefix(CALLBACK_OPEN_PREFIX))
    elif data.startswith(CALLBACK_ADMIN_PREFIX):
        await handle_admin_callback(update, context, data.removeprefix(CALLBACK_ADMIN_PREFIX))


async def show_home(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    repository = get_repository(context)
    await send_or_edit(
        update,
        context,
        format_home_text(repository),
        guide_keyboard(repository.root_nodes()),
    )


async def show_node(update: Update, context: ContextTypes.DEFAULT_TYPE, node_id: str) -> None:
    repository = get_repository(context)
    try:
        node = repository.get(node_id)
    except ContentError:
        await send_or_edit(update, context, "Раздел не найден. Вернитесь в главное меню.", home_keyboard())
        return

    await send_or_edit(update, context, format_node_text(node), node_keyboard(repository, node))
    await send_media_assets(update, context, node.media)


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await ensure_admin(update, context):
        return
    context.user_data.pop("awaiting_admin_body_for", None)
    await require_message(update).reply_text(
        "<b>Панель владельца</b>\n\n"
        "Здесь можно отредактировать текст разделов или перечитать JSON-файл после правок в репозитории.",
        parse_mode=ParseMode.HTML,
        reply_markup=admin_home_keyboard(),
    )


async def reload_content_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await ensure_admin(update, context):
        return
    await reload_content(update, context)


async def content_ids_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await ensure_admin(update, context):
        return
    await send_content_ids(update, context)


async def settext_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await ensure_admin(update, context):
        return
    message = require_message(update)
    command_text = message.text or ""
    _, _, payload = command_text.partition(" ")
    node_id_line, separator, body = payload.partition("\n")

    node_id = node_id_line.strip()
    if not node_id or not separator or not body.strip():
        await message.reply_text(
            "Формат:\n<code>/settext section_id\nНовый текст раздела</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    await update_node_body(update, context, node_id=node_id, body=body)


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop("awaiting_admin_body_for", None)
    await require_message(update).reply_text("Действие отменено.")


async def admin_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    node_id = context.user_data.get("awaiting_admin_body_for")
    if not node_id:
        return
    if not await ensure_admin(update, context):
        context.user_data.pop("awaiting_admin_body_for", None)
        return

    body = require_message(update).text or ""
    context.user_data.pop("awaiting_admin_body_for", None)
    await update_node_body(update, context, node_id=node_id, body=body)


async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    if not await ensure_admin(update, context):
        return

    if action == "home":
        await send_or_edit(
            update,
            context,
            "<b>Панель владельца</b>\n\nВыберите действие.",
            admin_home_keyboard(),
        )
    elif action == "reload":
        await reload_content(update, context)
    elif action == "ids":
        await send_content_ids(update, context)
    elif action == "edit_root":
        repository = get_repository(context)
        await send_or_edit(
            update,
            context,
            "<b>Редактирование</b>\n\nВыберите раздел.",
            admin_children_keyboard(repository.root_nodes(), parent_callback="home"),
        )
    elif action.startswith("children:"):
        repository = get_repository(context)
        node_id = action.removeprefix("children:")
        node = repository.get(node_id)
        await send_or_edit(
            update,
            context,
            f"<b>{html.escape(node.title)}</b>\n\nВыберите подраздел.",
            admin_children_keyboard(repository.children(node.id), parent_callback=f"node:{node.id}"),
        )
    elif action.startswith("node:"):
        repository = get_repository(context)
        node_id = action.removeprefix("node:")
        node = repository.get(node_id)
        await send_or_edit(update, context, format_admin_node_text(node), admin_node_keyboard(node))
    elif action.startswith("editbody:"):
        node_id = action.removeprefix("editbody:")
        node = get_repository(context).get(node_id)
        context.user_data["awaiting_admin_body_for"] = node.id
        await send_or_edit(
            update,
            context,
            (
                f"<b>Новый текст для раздела:</b> {html.escape(node.title)}\n\n"
                "Отправьте следующим сообщением полный новый текст. "
                "Для отмены используйте /cancel."
            ),
            InlineKeyboardMarkup(
                [[InlineKeyboardButton("Отмена", callback_data=f"{CALLBACK_ADMIN_PREFIX}node:{node.id}")]]
            ),
        )


async def update_node_body(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    node_id: str,
    body: str,
) -> None:
    repository = get_repository(context)
    try:
        node = repository.update_body(node_id, body)
    except ContentError as exc:
        await send_plain(update, context, f"Не удалось обновить раздел: {exc}")
        return

    await send_plain(update, context, f"Текст раздела «{node.title}» обновлен.")


async def reload_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        get_repository(context).reload()
    except ContentError as exc:
        await send_plain(update, context, f"Ошибка в контенте: {exc}")
        return
    await send_plain(update, context, "Контент перечитан из файла.")


async def send_content_ids(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    repository = get_repository(context)
    lines = ["<b>ID разделов</b>"]
    for node in repository.all_nodes():
        lines.append(f"<code>{html.escape(node.id)}</code> - {html.escape(node.title)}")
    await send_plain(update, context, "\n".join(lines), parse_mode=ParseMode.HTML)


async def send_media_assets(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    media_assets: tuple[MediaAsset, ...],
) -> None:
    if not media_assets:
        return

    config = get_config(context)
    chat_id = get_chat_id(update)
    if chat_id is None:
        return

    for asset in media_assets:
        media_path = resolve_media_path(config.media_root, asset)
        if media_path is None or not media_path.exists():
            logger.warning("Media file is missing or unsafe: %s", asset.path)
            continue

        caption = asset.caption or None
        with media_path.open("rb") as file:
            if asset.type == "photo":
                await context.bot.send_photo(chat_id=chat_id, photo=file, caption=caption)
            elif asset.type == "video":
                await context.bot.send_video(chat_id=chat_id, video=file, caption=caption)


def guide_keyboard(nodes: list[GuideNode]) -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(node.title, callback_data=f"{CALLBACK_OPEN_PREFIX}{node.id}")] for node in nodes]
    return InlineKeyboardMarkup(buttons)


def node_keyboard(repository: ContentRepository, node: GuideNode) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(child.title, callback_data=f"{CALLBACK_OPEN_PREFIX}{child.id}")]
        for child in repository.children(node.id)
    ]

    if node.parent_id:
        buttons.append([InlineKeyboardButton("Назад", callback_data=f"{CALLBACK_OPEN_PREFIX}{node.parent_id}")])
    else:
        buttons.append([InlineKeyboardButton("Главное меню", callback_data=CALLBACK_HOME)])
    return InlineKeyboardMarkup(buttons)


def home_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("Главное меню", callback_data=CALLBACK_HOME)]])


def admin_home_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Редактировать текст", callback_data=f"{CALLBACK_ADMIN_PREFIX}edit_root")],
            [InlineKeyboardButton("Показать ID разделов", callback_data=f"{CALLBACK_ADMIN_PREFIX}ids")],
            [InlineKeyboardButton("Перечитать content/guide.json", callback_data=f"{CALLBACK_ADMIN_PREFIX}reload")],
        ]
    )


def admin_children_keyboard(nodes: list[GuideNode], *, parent_callback: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(node.title, callback_data=f"{CALLBACK_ADMIN_PREFIX}node:{node.id}")]
        for node in nodes
    ]
    buttons.append([InlineKeyboardButton("Назад", callback_data=f"{CALLBACK_ADMIN_PREFIX}{parent_callback}")])
    return InlineKeyboardMarkup(buttons)


def admin_node_keyboard(node: GuideNode) -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton("Изменить текст", callback_data=f"{CALLBACK_ADMIN_PREFIX}editbody:{node.id}")]]
    if node.has_children:
        buttons.append([InlineKeyboardButton("Подразделы", callback_data=f"{CALLBACK_ADMIN_PREFIX}children:{node.id}")])
    buttons.append([InlineKeyboardButton("К списку разделов", callback_data=f"{CALLBACK_ADMIN_PREFIX}edit_root")])
    return InlineKeyboardMarkup(buttons)


def format_home_text(repository: ContentRepository) -> str:
    return f"<b>{html.escape(repository.title)}</b>\n\n{html.escape(repository.welcome)}"


def format_node_text(node: GuideNode) -> str:
    body = html.escape(node.body) if node.body else "Выберите подраздел ниже."
    return f"<b>{html.escape(node.title)}</b>\n\n{body}"


def format_admin_node_text(node: GuideNode) -> str:
    preview = node.body[:1200] + ("..." if len(node.body) > 1200 else "")
    if not preview:
        preview = "Текст пока не заполнен."
    return (
        f"<b>{html.escape(node.title)}</b>\n"
        f"<code>{html.escape(node.id)}</code>\n\n"
        f"{html.escape(preview)}"
    )


async def send_or_edit(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    chunks = split_text(text)
    first_chunk = chunks[0]
    query = update.callback_query
    if query is not None and query.message is not None:
        try:
            await query.edit_message_text(
                first_chunk,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup if len(chunks) == 1 else None,
            )
        except BadRequest as exc:
            if "Message is not modified" not in str(exc):
                raise
    else:
        await require_message(update).reply_text(
            first_chunk,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup if len(chunks) == 1 else None,
        )

    if len(chunks) > 1:
        chat_id = get_chat_id(update)
        for chunk in chunks[1:-1]:
            await context.bot.send_message(chat_id=chat_id, text=chunk, parse_mode=ParseMode.HTML)
        await context.bot.send_message(
            chat_id=chat_id,
            text=chunks[-1],
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
        )


async def send_plain(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    *,
    parse_mode: str | None = None,
) -> None:
    query = update.callback_query
    if query is not None and query.message is not None:
        await query.message.reply_text(text, parse_mode=parse_mode)
        return
    await require_message(update).reply_text(text, parse_mode=parse_mode)


def split_text(text: str) -> list[str]:
    if len(text) <= MAX_MESSAGE_LENGTH:
        return [text]

    chunks: list[str] = []
    current = ""
    for paragraph in text.split("\n\n"):
        candidate = f"{current}\n\n{paragraph}" if current else paragraph
        if len(candidate) <= MAX_MESSAGE_LENGTH:
            current = candidate
            continue
        if current:
            chunks.append(current)
        while len(paragraph) > MAX_MESSAGE_LENGTH:
            chunks.append(paragraph[:MAX_MESSAGE_LENGTH])
            paragraph = paragraph[MAX_MESSAGE_LENGTH:]
        current = paragraph
    if current:
        chunks.append(current)
    return chunks


def resolve_media_path(media_root: Path, asset: MediaAsset) -> Path | None:
    media_root = media_root.resolve()
    candidate = (media_root / asset.path).resolve()
    try:
        common_path = os.path.commonpath([media_root, candidate])
    except ValueError:
        return None
    if common_path != str(media_root):
        return None
    return candidate


def get_repository(context: ContextTypes.DEFAULT_TYPE) -> ContentRepository:
    return context.application.bot_data["content"]


def get_config(context: ContextTypes.DEFAULT_TYPE) -> BotConfig:
    return context.application.bot_data["config"]


def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    config = get_config(context)
    user = update.effective_user
    return bool(config.admin_telegram_id and user and user.id == config.admin_telegram_id)


async def ensure_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if is_admin(update, context):
        return True
    await send_plain(update, context, "Команда доступна только владельцу бота.")
    return False


def require_message(update: Update):
    if update.message is None:
        raise RuntimeError("Update has no message.")
    return update.message


def get_chat_id(update: Update) -> int | None:
    if update.effective_chat is not None:
        return update.effective_chat.id
    if update.callback_query is not None and update.callback_query.message is not None:
        return update.callback_query.message.chat_id
    return None


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled Telegram bot error", exc_info=context.error)


def main() -> None:
    application = build_application(load_config())
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
