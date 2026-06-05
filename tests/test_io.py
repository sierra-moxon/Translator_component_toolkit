"""Tests for the output serializer and exit-code constants."""

import pandas as pd

from translator_component_toolkit.io import (
    EXIT_NOT_FOUND,
    EXIT_OK,
    EXIT_UNEXPECTED,
    EXIT_UPSTREAM,
    EXIT_USAGE,
    paginate,
    serialize,
)
from translator_component_toolkit.translator_node import TranslatorNode


def test_primitives_pass_through():
    assert serialize("a") == "a"
    assert serialize(3) == 3
    assert serialize(1.5) == 1.5
    assert serialize(True) is True
    assert serialize(None) is None


def test_dataclass_serializes_to_dict():
    node = TranslatorNode(curie="MONDO:1", label="x", types=["biolink:Disease"])
    result = serialize(node)
    assert result["curie"] == "MONDO:1"
    assert result["label"] == "x"
    assert result["types"] == ["biolink:Disease"]


def test_dataframe_serializes_to_records():
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    result = serialize(df)
    assert result == [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}]


def test_tuple_becomes_list():
    assert serialize((1, 2, 3)) == [1, 2, 3]


def test_nested_structures_are_serialized():
    node = TranslatorNode(curie="C:1")
    payload = {"nodes": [node], "meta": ("a", "b")}
    result = serialize(payload)
    assert result["nodes"][0]["curie"] == "C:1"
    assert result["meta"] == ["a", "b"]


def test_dict_keys_coerced_to_str():
    assert serialize({1: "a"}) == {"1": "a"}


def test_unknown_object_falls_back_to_str():
    class Weird:
        def __str__(self):
            return "weird"

    assert serialize(Weird()) == "weird"


def test_exit_codes_are_distinct():
    codes = {EXIT_OK, EXIT_USAGE, EXIT_NOT_FOUND, EXIT_UPSTREAM, EXIT_UNEXPECTED}
    assert len(codes) == 5
    assert EXIT_OK == 0


def test_paginate_limit_truncates_and_sets_metadata():
    env = paginate(list(range(10)), limit=3, offset=0)
    assert env["data"] == [0, 1, 2]
    assert env["total"] == 10
    assert env["returned"] == 3
    assert env["truncated"] is True
    assert env["next_offset"] == 3


def test_paginate_offset_advances_window():
    env = paginate(list(range(10)), limit=3, offset=3)
    assert env["data"] == [3, 4, 5]
    assert env["next_offset"] == 6


def test_paginate_last_page_is_not_truncated():
    env = paginate(list(range(5)), limit=3, offset=3)
    assert env["data"] == [3, 4]
    assert env["truncated"] is False
    assert env["next_offset"] is None


def test_paginate_no_limit_returns_everything():
    env = paginate(list(range(4)))
    assert env["data"] == [0, 1, 2, 3]
    assert env["total"] == 4
    assert env["truncated"] is False
    assert env["next_offset"] is None


def test_paginate_serializes_dataframe_records():
    df = pd.DataFrame({"a": [1, 2, 3]})
    env = paginate(df, limit=2)
    assert env["data"] == [{"a": 1}, {"a": 2}]
    assert env["total"] == 3
    assert env["truncated"] is True


def test_paginate_wraps_non_list_as_single_item():
    env = paginate({"k": "v"})
    assert env["data"] == [{"k": "v"}]
    assert env["total"] == 1
