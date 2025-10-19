"""Filesystem layout utilities."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from .config import Config
from .util import io


@dataclass(slots=True)
class PathManager:
    """Helper for structured output paths."""

    config: Config

    def run_root(self) -> Path:
        return self.config.out_dir / self.config.run_label()

    def ensure(self) -> Path:
        root = self.run_root()
        root.mkdir(parents=True, exist_ok=True)
        return root

    def subdir(self, *parts: str) -> Path:
        path = self.run_root().joinpath(*parts)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def path(self, *parts: str) -> Path:
        path = self.run_root().joinpath(*parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    # Common directories
    def meta_dir(self) -> Path:
        return self.subdir("meta")

    def sources_dir(self) -> Path:
        return self.subdir("sources")

    def combined_dir(self) -> Path:
        return self.subdir("combined")

    def live_dir(self) -> Path:
        return self.subdir("live")

    def out_of_scope_dir(self) -> Path:
        return self.subdir("out_of_scope")

    def write_json(self, relative: str, payload: object) -> Path:
        path = self.path(relative)
        io.write_json(path, payload)
        return path

    def write_text(self, relative: str, content: str) -> Path:
        path = self.path(relative)
        io.write_text(path, content)
        return path

    def write_lines(self, relative: str, lines: list[str]) -> Path:
        path = self.path(relative)
        io.write_lines(path, lines)
        return path

    def mirror_to_out_of_scope(self, relative: str) -> Path:
        base = self.path(relative)
        oos = self.out_of_scope_dir().joinpath(*Path(relative).parts)
        if base.exists():
            data = base.read_bytes()
            io.write_text(oos, data.decode("utf-8"))
        return oos


def write_run_info(fs: PathManager) -> None:
    config = fs.config
    meta = fs.meta_dir()
    io.write_json(meta / "run_info.json", {
        "target": config.target,
        "program": config.program_name,
        "modules": config.enabled_modules(),
        "timeout": config.timeout,
        "threads": config.threads,
        "rate": config.rate,
    })


def write_environment(fs: PathManager, tools: Mapping[str, object]) -> None:
    import platform
    payload = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "tools": tools,
    }
    io.write_json(fs.meta_dir() / "environment.json", payload)


def write_tools(fs: PathManager, tools: Mapping[str, object]) -> None:
    io.write_json(fs.meta_dir() / "tools.json", tools)
