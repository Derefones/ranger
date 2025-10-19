from __future__ import annotations

from ranger.scope import build_scope


def test_default_scope_target_inclusion() -> None:
    scope = build_scope("example.com", None, None)
    in_scope, out_scope = scope.partition_scope(["www.example.com", "other.org"])
    assert "www.example.com" in in_scope
    assert "other.org" in out_scope
