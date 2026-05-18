"""Unit tests for the hash-chain primitives.

These tests are the strongest contract we ship: if any of these regress,
manifest verification across runs will silently break. They are intentionally
strict.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from asp_benchmark.hasher import (
    FileHash,
    HashTreeLeaf,
    build_manifest_hash,
    canonical_json,
    hash_bytes,
    hash_file,
    hash_json,
    walk_files,
)


def test_hash_bytes_is_deterministic():
    """sha256 is deterministic — sanity check our wrapper preserves that."""
    assert hash_bytes(b"hello") == hash_bytes(b"hello")
    assert hash_bytes(b"hello") != hash_bytes(b"hellp")


def test_hash_bytes_known_value():
    """Pin one known sha256 so future encoding accidents (e.g. switching
    to base64) are caught."""
    # echo -n "hello" | sha256sum
    assert hash_bytes(b"hello") == (
        "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    )


def test_canonical_json_sorts_keys():
    """Hashes must be stable across dict insertion orders."""
    a = canonical_json({"b": 1, "a": 2})
    b = canonical_json({"a": 2, "b": 1})
    assert a == b
    # And it's actually sorted.
    assert a == b'{"a":2,"b":1}'


def test_canonical_json_compact():
    """No whitespace — pretty-printing would silently change hashes."""
    assert canonical_json({"a": 1, "b": [1, 2]}) == b'{"a":1,"b":[1,2]}'


def test_canonical_json_utf8():
    """Non-ASCII content must round-trip as UTF-8, not escape sequences."""
    blob = canonical_json({"greeting": "olá"})
    assert "olá".encode("utf-8") in blob


def test_hash_json_matches_hash_canonical_bytes():
    obj = {"a": 1, "nested": {"b": [1, 2, 3]}}
    assert hash_json(obj) == hash_bytes(canonical_json(obj))


def test_hash_file_matches_hash_bytes(tmp_path: Path):
    f = tmp_path / "x.bin"
    payload = b"some content with binary \x00 inside"
    f.write_bytes(payload)
    assert hash_file(f) == hash_bytes(payload)


def test_walk_files_is_sorted(tmp_path: Path):
    """walk_files must impose a deterministic order so two filesystems
    that disagree on iterdir() give the same hash tree."""
    (tmp_path / "z.txt").write_text("z")
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.txt").write_text("b")
    paths = walk_files(tmp_path)
    names = [str(p.relative_to(tmp_path)) for p in paths]
    # Sub-directory contents come grouped because path sort is lexicographic
    # by full string, so "sub/b.txt" sorts after "z.txt". This is fine as
    # long as the order is deterministic.
    assert names == sorted(names)


def test_hash_tree_leaf_independent_of_add_order(tmp_path: Path):
    """Adding files in different orders must produce the same leaf hash."""
    (tmp_path / "a.txt").write_text("alpha")
    (tmp_path / "b.txt").write_text("beta")

    leaf1 = HashTreeLeaf(name="inputs")
    leaf1.add_file(tmp_path, tmp_path / "a.txt")
    leaf1.add_file(tmp_path, tmp_path / "b.txt")

    leaf2 = HashTreeLeaf(name="inputs")
    leaf2.add_file(tmp_path, tmp_path / "b.txt")
    leaf2.add_file(tmp_path, tmp_path / "a.txt")

    assert leaf1.leaf_hash() == leaf2.leaf_hash()


def test_hash_tree_leaf_changes_on_byte_flip(tmp_path: Path):
    """Tamper detection: editing one byte must change the leaf hash."""
    (tmp_path / "a.txt").write_text("alpha")
    leaf1 = HashTreeLeaf(name="inputs")
    leaf1.add_file(tmp_path, tmp_path / "a.txt")
    h1 = leaf1.leaf_hash()

    (tmp_path / "a.txt").write_text("alphb")  # one-byte flip
    leaf2 = HashTreeLeaf(name="inputs")
    leaf2.add_file(tmp_path, tmp_path / "a.txt")
    h2 = leaf2.leaf_hash()

    assert h1 != h2


def test_manifest_hash_independent_of_leaf_order(tmp_path: Path):
    (tmp_path / "a.txt").write_text("alpha")
    env = HashTreeLeaf(name="env")
    env.add_file(tmp_path, tmp_path / "a.txt")
    inputs = HashTreeLeaf(name="inputs")

    h1 = build_manifest_hash([env, inputs])
    h2 = build_manifest_hash([inputs, env])
    assert h1 == h2


def test_manifest_hash_changes_when_any_leaf_changes(tmp_path: Path):
    (tmp_path / "a.txt").write_text("alpha")
    env = HashTreeLeaf(name="env")
    env.add_file(tmp_path, tmp_path / "a.txt")

    inputs1 = HashTreeLeaf(name="inputs")
    inputs1.add_file(tmp_path, tmp_path / "a.txt")

    h_before = build_manifest_hash([env, inputs1])

    # Edit the file; both `env` (which references it) and `inputs1` will
    # hash differently next walk. Create a fresh leaf to reflect that.
    (tmp_path / "a.txt").write_text("alpha2")
    inputs2 = HashTreeLeaf(name="inputs")
    inputs2.add_file(tmp_path, tmp_path / "a.txt")
    env2 = HashTreeLeaf(name="env")
    env2.add_file(tmp_path, tmp_path / "a.txt")

    h_after = build_manifest_hash([env2, inputs2])
    assert h_before != h_after


def test_file_hash_round_trip_dict(tmp_path: Path):
    """FileHash.as_dict() preserves all three reproducibility fields."""
    (tmp_path / "x.txt").write_text("hello world")
    fh = FileHash.from_file(tmp_path, tmp_path / "x.txt")
    d = fh.as_dict()
    assert set(d) == {"relative_path", "sha256", "size_bytes"}
    assert d["relative_path"] == "x.txt"
    assert d["size_bytes"] == len(b"hello world")
    assert d["sha256"] == hash_bytes(b"hello world")
