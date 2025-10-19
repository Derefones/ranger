from __future__ import annotations

from pathlib import Path

from ranger.scope import build_scope


def test_scope_inclusion_and_exclusion(tmp_path: Path) -> None:
    include = tmp_path / "include.yaml"
    include.write_text(
        """
        domains:
          - "*.example.com"
        urls:
          - "https://api.example.com/"
        """.strip()
    )
    exclude = tmp_path / "exclude.yaml"
    exclude.write_text(
        """
        domains:
          - "admin.example.com"
        cidrs:
          - "10.0.0.0/8"
        """.strip()
    )
    scope = build_scope("example.com", include, exclude)
    assert scope.is_in_scope("www.example.com")
    assert not scope.is_in_scope("admin.example.com")
    assert scope.is_oos("10.0.0.1")
    in_scope, out_scope = scope.partition_scope(["www.example.com", "admin.example.com"])
    assert in_scope == ["www.example.com"]
    assert out_scope == ["admin.example.com"]
