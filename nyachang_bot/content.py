"""Content loading and editing for the Nha Trang guide."""

from __future__ import annotations

import json
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


NODE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]{0,39}$")
SUPPORTED_MEDIA_TYPES = {"photo", "video"}


class ContentError(ValueError):
    """Raised when guide content is malformed."""


@dataclass(frozen=True)
class MediaAsset:
    type: str
    path: str
    caption: str = ""


@dataclass(frozen=True)
class GuideNode:
    id: str
    title: str
    body: str
    media: tuple[MediaAsset, ...]
    parent_id: str | None
    children_ids: tuple[str, ...]

    @property
    def has_children(self) -> bool:
        return bool(self.children_ids)


class ContentRepository:
    """Read and update a tree-shaped JSON guide."""

    def __init__(self, content_file: Path) -> None:
        self.content_file = content_file
        self._raw: dict[str, Any] = {}
        self._nodes: dict[str, GuideNode] = {}
        self._root_ids: tuple[str, ...] = ()

    @property
    def title(self) -> str:
        return str(self._raw.get("title") or "Гид по Нячангу")

    @property
    def welcome(self) -> str:
        return str(self._raw.get("welcome") or "Выберите раздел:")

    def reload(self) -> None:
        if not self.content_file.exists():
            raise ContentError(f"Content file does not exist: {self.content_file}")

        with self.content_file.open("r", encoding="utf-8") as file:
            raw = json.load(file)

        if not isinstance(raw, dict):
            raise ContentError("Top-level content must be a JSON object.")

        nodes: dict[str, GuideNode] = {}
        root_items = raw.get("items")
        if not isinstance(root_items, list):
            raise ContentError("Top-level 'items' must be a list.")

        root_ids = tuple(self._parse_node(item, parent_id=None, nodes=nodes) for item in root_items)
        self._raw = raw
        self._nodes = nodes
        self._root_ids = root_ids

    def root_nodes(self) -> list[GuideNode]:
        return [self._nodes[node_id] for node_id in self._root_ids]

    def children(self, node_id: str) -> list[GuideNode]:
        node = self.get(node_id)
        return [self._nodes[child_id] for child_id in node.children_ids]

    def get(self, node_id: str) -> GuideNode:
        try:
            return self._nodes[node_id]
        except KeyError as exc:
            raise ContentError(f"Unknown content node: {node_id}") from exc

    def all_nodes(self) -> list[GuideNode]:
        return list(self._nodes.values())

    def update_body(self, node_id: str, body: str) -> GuideNode:
        if node_id not in self._nodes:
            raise ContentError(f"Unknown content node: {node_id}")

        changed = self._set_body(self._raw["items"], node_id=node_id, body=body)
        if not changed:
            raise ContentError(f"Could not update content node: {node_id}")

        self._write_raw()
        self.reload()
        return self.get(node_id)

    def _write_raw(self) -> None:
        self.content_file.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=self.content_file.parent,
            delete=False,
            prefix=f".{self.content_file.name}.",
        ) as file:
            json.dump(self._raw, file, ensure_ascii=False, indent=2)
            file.write("\n")
            temporary_path = Path(file.name)
        temporary_path.replace(self.content_file)

    def _parse_node(self, item: Any, *, parent_id: str | None, nodes: dict[str, GuideNode]) -> str:
        if not isinstance(item, dict):
            raise ContentError("Every guide item must be a JSON object.")

        node_id = self._read_node_id(item)
        if node_id in nodes:
            raise ContentError(f"Duplicate guide item id: {node_id}")

        title = item.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ContentError(f"Guide item '{node_id}' must have a non-empty title.")

        body = item.get("body", "")
        if not isinstance(body, str):
            raise ContentError(f"Guide item '{node_id}' body must be a string.")

        media = tuple(self._parse_media(asset, node_id=node_id) for asset in item.get("media", []))

        child_items = item.get("children", [])
        if not isinstance(child_items, list):
            raise ContentError(f"Guide item '{node_id}' children must be a list.")

        nodes[node_id] = GuideNode(
            id=node_id,
            title=title.strip(),
            body=body.strip(),
            media=media,
            parent_id=parent_id,
            children_ids=(),
        )
        child_ids = tuple(self._parse_node(child, parent_id=node_id, nodes=nodes) for child in child_items)
        nodes[node_id] = GuideNode(
            id=node_id,
            title=title.strip(),
            body=body.strip(),
            media=media,
            parent_id=parent_id,
            children_ids=child_ids,
        )
        return node_id

    @staticmethod
    def _read_node_id(item: dict[str, Any]) -> str:
        node_id = item.get("id")
        if not isinstance(node_id, str) or not NODE_ID_RE.fullmatch(node_id):
            raise ContentError(
                "Guide item id must be 1-40 characters: lowercase latin letters, digits, '.', '_' or '-'."
            )
        return node_id

    @staticmethod
    def _parse_media(asset: Any, *, node_id: str) -> MediaAsset:
        if not isinstance(asset, dict):
            raise ContentError(f"Media asset in '{node_id}' must be a JSON object.")

        asset_type = asset.get("type")
        if asset_type not in SUPPORTED_MEDIA_TYPES:
            raise ContentError(f"Media asset in '{node_id}' must have type: photo or video.")

        asset_path = asset.get("path")
        if not isinstance(asset_path, str) or not asset_path.strip():
            raise ContentError(f"Media asset in '{node_id}' must have a path.")

        path = Path(asset_path)
        if path.is_absolute() or ".." in path.parts:
            raise ContentError(f"Media asset in '{node_id}' must use a safe relative path.")

        caption = asset.get("caption", "")
        if not isinstance(caption, str):
            raise ContentError(f"Media asset caption in '{node_id}' must be a string.")

        return MediaAsset(type=asset_type, path=asset_path.strip(), caption=caption.strip())

    @classmethod
    def _set_body(cls, items: list[Any], *, node_id: str, body: str) -> bool:
        for item in items:
            if not isinstance(item, dict):
                continue
            if item.get("id") == node_id:
                item["body"] = body.strip()
                return True
            children = item.get("children")
            if isinstance(children, list) and cls._set_body(children, node_id=node_id, body=body):
                return True
        return False
