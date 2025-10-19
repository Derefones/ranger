from __future__ import annotations

import json
from pathlib import Path

from ranger.parsers.ffuf import parse_ffuf
from ranger.parsers.generic import iter_csv, iter_jsonl
from ranger.parsers.httpx import parse_httpx
from ranger.parsers.nmap import parse_nmap
from ranger.parsers.nuclei import parse_nuclei
from ranger.parsers.subzy import parse_subzy


def test_parse_httpx() -> None:
    payload = {
        "host": "example.com",
        "port": 443,
        "scheme": "https",
        "status": 200,
        "title": "Example",
        "tech": "",
        "fingerprint": "",
        "tls": "",
        "cdn": "",
    }
    lines = [json.dumps(payload)]
    rows = parse_httpx(lines)
    assert rows[0]["host"] == "example.com"
    assert rows[0]["status"] == 200


def test_parse_nuclei() -> None:
    nuclei_payload = {
        "templateID": "test",
        "info": {"name": "Test", "severity": "low"},
        "host": "https://example.com",
        "matched-at": "https://example.com",
        "matcher-status": "matched",
    }
    lines = [json.dumps(nuclei_payload)]
    rows = parse_nuclei(lines)
    assert rows[0]["template_id"] == "test"
    assert rows[0]["severity"] == "low"


def test_generic_csv(tmp_path: Path) -> None:
    path = tmp_path / "data.csv"
    path.write_text("a,b\n1,2\n", encoding="utf-8")
    rows = list(iter_csv(path))
    assert rows[0]["a"] == "1"


def test_generic_jsonl(tmp_path: Path) -> None:
    path = tmp_path / "data.jsonl"
    path.write_text('{"a": 1}\n', encoding="utf-8")
    rows = list(iter_jsonl(path))
    assert rows[0]["a"] == 1


def test_parse_ffuf(tmp_path: Path) -> None:
    path = tmp_path / "ffuf.csv"
    path.write_text("url,status\nhttps://example.com,200\n", encoding="utf-8")
    rows = parse_ffuf(str(path))
    assert rows[0]["status"] == "200"


def test_parse_subzy(tmp_path: Path) -> None:
    path = tmp_path / "subzy.csv"
    path.write_text("host,verified\nexample.com,true\n", encoding="utf-8")
    rows = parse_subzy(str(path))
    assert rows[0]["verified"] == "True"


def test_parse_nmap(tmp_path: Path) -> None:
    xml = (
        "<nmaprun><host><address addr=\"example.com\"/>"
        "<ports><port portid=\"80\" protocol=\"tcp\"/></ports>"
        "</host></nmaprun>"
    )
    path = tmp_path / "nmap.xml"
    path.write_text(xml, encoding="utf-8")
    rows = parse_nmap(str(path))
    assert rows[0]["port"] == "80"
