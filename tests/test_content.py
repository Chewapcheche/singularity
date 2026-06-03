from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from nyachang_bot.content import ContentError, ContentRepository


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ContentRepositoryTest(unittest.TestCase):
    def test_loads_bundled_guide(self) -> None:
        repository = ContentRepository(PROJECT_ROOT / "content" / "guide.json")
        repository.reload()

        self.assertGreaterEqual(len(repository.root_nodes()), 3)
        self.assertEqual(repository.get("relocation.documents").parent_id, "relocation")

    def test_updates_nested_body_and_persists_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            content_file = Path(directory) / "guide.json"
            shutil.copyfile(PROJECT_ROOT / "content" / "guide.json", content_file)
            repository = ContentRepository(content_file)
            repository.reload()

            repository.update_body("city-guide.mobile", "Новый текст про связь.")

            reloaded = ContentRepository(content_file)
            reloaded.reload()
            self.assertEqual(reloaded.get("city-guide.mobile").body, "Новый текст про связь.")

    def test_rejects_duplicate_ids_in_ancestor_chain(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            content_file = Path(directory) / "guide.json"
            content_file.write_text(
                json.dumps(
                    {
                        "items": [
                            {
                                "id": "same",
                                "title": "Parent",
                                "children": [{"id": "same", "title": "Child"}],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            repository = ContentRepository(content_file)
            with self.assertRaises(ContentError):
                repository.reload()

    def test_rejects_unsafe_media_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            content_file = Path(directory) / "guide.json"
            content_file.write_text(
                json.dumps(
                    {
                        "items": [
                            {
                                "id": "media",
                                "title": "Media",
                                "media": [{"type": "photo", "path": "../secret.jpg"}],
                                "children": [],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            repository = ContentRepository(content_file)
            with self.assertRaises(ContentError):
                repository.reload()


if __name__ == "__main__":
    unittest.main()
