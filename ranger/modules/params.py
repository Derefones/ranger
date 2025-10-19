"""Parameter analysis placeholder."""
from __future__ import annotations

from ..util import io
from . import ModuleContext, ModuleOutcome


def run(context: ModuleContext) -> ModuleOutcome:
    outcome = ModuleOutcome(name="params")
    urls_path = context.fs.combined_dir() / "urls.txt"
    if not urls_path.exists():
        outcome.errors.append("no urls")
        return outcome
    lines = urls_path.read_text(encoding="utf-8").splitlines()
    urls = [line.strip() for line in lines if line.strip()]
    params_dir = context.fs.subdir("params")
    with_params = [url for url in urls if "?" in url]
    io.write_lines(params_dir / "urls_with_params.txt", with_params)
    gf_dir = params_dir / "gf"
    gf_dir.mkdir(parents=True, exist_ok=True)
    wordlists_dir = params_dir / "wordlists"
    wordlists_dir.mkdir(parents=True, exist_ok=True)
    io.write_lines(wordlists_dir / "derived.txt", [])
    outcome.artifacts["urls_with_params"] = str(params_dir / "urls_with_params.txt")
    outcome.counts["urls"] = len(urls)
    outcome.counts["with_params"] = len(with_params)
    return outcome
