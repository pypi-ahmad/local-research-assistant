"""External source connectors for websites, GitHub, and YouTube."""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from git import Repo


class ConnectorService:
    """Connectors for remote source ingestion."""

    async def fetch_website_text(self, url: str) -> tuple[str, bytes]:
        """Fetch website and extract readable text."""
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            html = response.text

        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n")
        filename = self._safe_filename(url, suffix=".txt")
        return filename, text.encode("utf-8")

    async def fetch_github_repo_snapshot(self, url: str) -> tuple[str, bytes]:
        """Clone repository shallow and extract markdown/text corpus."""
        with tempfile.TemporaryDirectory(prefix="lra-git-") as tmp_dir:
            repo_dir = Path(tmp_dir) / "repo"
            Repo.clone_from(url, repo_dir, depth=1)

            files = list(repo_dir.rglob("*.md")) + list(repo_dir.rglob("*.txt"))
            if not files:
                files = list(repo_dir.glob("README*"))

            parts: list[str] = []
            for path in files[:200]:
                try:
                    content = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    content = path.read_text(encoding="latin-1", errors="ignore")
                parts.append(f"\n# File: {path.relative_to(repo_dir)}\n{content}\n")

        filename = self._safe_filename(url, suffix=".md")
        return filename, "\n".join(parts).encode("utf-8")

    async def fetch_youtube_transcript(self, url: str) -> tuple[str, bytes]:
        """Fetch transcript with local yt-dlp command."""
        with tempfile.TemporaryDirectory(prefix="lra-yt-") as tmp_dir:
            cmd = [
                shutil.which("yt-dlp") or "yt-dlp",
                "--skip-download",
                "--write-auto-sub",
                "--sub-lang",
                "en",
                "--convert-subs",
                "vtt",
                "-o",
                f"{tmp_dir}/%(id)s.%(ext)s",
                url,
            ]
            subprocess.run(cmd, check=True, capture_output=True, text=True)

            vtt_files = list(Path(tmp_dir).glob("*.vtt"))
            if not vtt_files:
                raise RuntimeError("No transcript generated")

            text = self._vtt_to_text(vtt_files[0].read_text(encoding="utf-8", errors="ignore"))

        filename = self._safe_filename(url, suffix=".txt")
        return filename, text.encode("utf-8")

    @staticmethod
    def _vtt_to_text(vtt: str) -> str:
        lines = []
        for line in vtt.splitlines():
            if "-->" in line or line.strip().isdigit() or line.strip().startswith("WEBVTT"):
                continue
            cleaned = line.strip()
            if cleaned:
                lines.append(cleaned)
        return "\n".join(lines)

    @staticmethod
    def _safe_filename(source: str, suffix: str) -> str:
        cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", source)[:120].strip("-")
        return f"{cleaned or 'source'}{suffix}"
