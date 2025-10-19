from __future__ import annotations

from pathlib import Path

from ranger.config import CLIArgs, Toolset, build_config
from ranger.fs import PathManager, write_run_info


def make_config(tmp_path: Path) -> PathManager:
    args = CLIArgs(
        target="example.com",
        program_name="example",
        include_scope=None,
        exclude_scope=None,
        out=tmp_path,
        rate=10.0,
        threads=4,
        timeout=30,
        modules=("all",),
        respect_robots=False,
        ffuf_wordlist=None,
        gf_patterns=None,
        nmap_top_ports=100,
        nuclei_templates=None,
        http_proxy=None,
        save_raw=False,
        dry_run=False,
        self_test=False,
    )
    config = build_config(args, Toolset())
    fs = PathManager(config)
    fs.ensure()
    return fs


def test_write_run_info(tmp_path: Path) -> None:
    fs = make_config(tmp_path)
    write_run_info(fs)
    run_info = fs.meta_dir() / "run_info.json"
    assert run_info.exists()
    content = run_info.read_text(encoding="utf-8")
    assert "example.com" in content
