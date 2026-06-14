import re
import tempfile
import unittest
from pathlib import Path

import app
from starlette.datastructures import Headers, UploadFile


def old_related_indexes(
    current_index: int,
    files: list[app.SourceFile],
) -> list[int]:
    current = files[current_index]
    candidates: list[tuple[str, int, bool]] = []
    for index, other in enumerate(files):
        if index == current_index:
            continue
        other_path = app.display_path(other)
        names = {
            other.label,
            app.export_label(other),
            other_path,
            Path(other_path).name,
            Path(other_path).stem,
        }
        for name in sorted(value for value in names if value):
            candidates.append((name, index, "/" in name or "." in name))

    related: list[int] = []
    seen_labels: set[str] = set()
    for needle, index, is_path_like in candidates:
        other = files[index]
        if other.label in seen_labels:
            continue
        pattern = re.escape(needle) if is_path_like else rf"\b{re.escape(needle)}\b"
        if re.search(pattern, current.content):
            related.append(index)
            seen_labels.add(other.label)
    return related


class ReferenceMatcherTest(unittest.TestCase):
    def test_matches_previous_reference_semantics(self) -> None:
        files = [
            app.SourceFile(
                label="start.md",
                origin="upload",
                suffix=".md",
                content="beta.md, gamma/plan.md und plan. Nicht: planet.",
                size_bytes=52,
                source_path="projekt/start.md",
            ),
            app.SourceFile(
                label="beta.md",
                origin="upload",
                suffix=".md",
                content="start",
                size_bytes=5,
                source_path="projekt/beta.md",
            ),
            app.SourceFile(
                label="plan.md",
                origin="upload",
                suffix=".md",
                content="",
                size_bytes=0,
                source_path="gamma/plan.md",
            ),
            app.SourceFile(
                label="plan",
                origin="upload",
                suffix=".md",
                content="",
                size_bytes=0,
                source_path="anderer/plan",
            ),
            app.SourceFile(
                label="plan",
                origin="upload",
                suffix=".md",
                content="",
                size_bytes=0,
                source_path="duplikat/plan",
            ),
        ]
        matcher = app.ReferenceMatcher(files)

        for index, file in enumerate(files):
            self.assertEqual(
                old_related_indexes(index, files),
                matcher.related_indexes(file.content, index, files),
            )


class MultipartExportTest(unittest.IsolatedAsyncioTestCase):
    async def test_exports_622_markdown_uploads(self) -> None:
        uploads = [
            UploadFile(
                file=tempfile.SpooledTemporaryFile(),
                filename=f"ordner/file-{index:03}.md",
                headers=Headers({"content-type": "text/markdown"}),
            )
            for index in range(622)
        ]
        for index, upload in enumerate(uploads):
            upload.file.write((f"# Datei {index}\n\nInhalt ohne Verweis.\n" * 20).encode())
            upload.file.seek(0)

        response = await app.convert(
            paths="",
            output="markdown",
            html_mode="markdown",
            uploads=uploads,
        )
        export_path = Path(response.path)
        try:
            self.assertEqual(200, response.status_code)
            self.assertIn("attachment;", response.headers["content-disposition"])
            self.assertGreater(export_path.stat().st_size, 100_000)
        finally:
            export_path.unlink(missing_ok=True)
            for upload in uploads:
                await upload.close()


if __name__ == "__main__":
    unittest.main()
