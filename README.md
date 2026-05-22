# Pokemon vs Dota TD

Оффлайн Tower Defense для ПК (не браузер): вид сверху с объёмными 3D-моделями. Защита — покемоны, враги — крипы из Dota 2 (стилизованные примитивы без сторонних ассетов).

## Возможности

- **10 уровней**; уровень 1 — **3 волны**; уровни 1–2 с пониженной сложностью
- **5 покемонов**-башен с разными характеристиками
- **Улучшение за XP** (уровни 2–4)
- **Крипы усиливаются** с номером волны и уровнем
- Полное **закрытие процесса** по ESC, кнопке Quit или крестику окна

## Запуск

```bash
pip install -r requirements.txt
python main.py
```

Или:

```bash
chmod +x run_game.sh
./run_game.sh
```

### Windows

```bat
pip install -r requirements.txt
python main.py
```

## Управление

| Действие | Клавиша / мышь |
|----------|----------------|
| Выбрать тип башни | Кнопки внизу экрана |
| Режим установки | **P** или кнопка Place |
| Поставить башню | **ЛКМ** на клетку (не на путь) |
| Выбрать башню | **ЛКМ** по башне |
| Улучшить | **U** или Upgrade |
| Продать | Sell |
| Выход | **ESC** / Quit / ✕ |

## Папка на рабочем столе + EXE (Windows)

**На вашем ПК** откройте папку с игрой (клон репозитория или скачанный архив) и:

1. Дважды щёлкните **`package_to_desktop.bat`** — скопирует файлы в  
   `%USERPROFILE%\Desktop\PokemonDotaTD`
2. Дважды щёлкните **`build_windows.bat`** в той же папке (или на рабочем столе) — соберёт **`PokemonDotaTD.exe`**
3. Запуск игры: двойной щелчок по **`PokemonDotaTD.exe`** на рабочем столе

Подробно: файл **`LAUNCH.txt`** в папке игры.

> EXE для Windows собирается **только на Windows** (PyInstaller). На Linux получается файл `PokemonDotaTD` без расширения `.exe`.

### Linux / macOS

```bash
chmod +x build_linux.sh package_to_desktop.sh
./build_linux.sh
# Игра: ~/Desktop/PokemonDotaTD/PokemonDotaTD
```

## Структура

- `main.py` — точка входа, цикл Ursina
- `game/config.py` — уровни, волны, баланс
- `game/entities.py` — башни, крипы, снаряды (пул)
- `game/waves.py` — спавн волн
- `game/app.py` — UI и логика матча

## Требования

- Python 3.10+
- OpenGL / видеодрайвер (для Ursina / Panda3D)
- Linux / Windows / macOS
