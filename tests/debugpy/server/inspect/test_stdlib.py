# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root
# for license information.

import pytest
import array
import collections

from debugpy.server.inspect.stdlib import ChildLen, ChildItem, SequenceInspector, MappingInspector, ListInspector

def test_ChildLen_expr():
    sequence = [1, 2, 3]
    child_len = ChildLen(sequence)
    expr_name = "sequence"
    assert child_len.expr(f"{expr_name}") == f"len({expr_name})"

key_value_test_data = [
    (1, 2), # ints
    ("foo", "bar"), # strings
    (1.0, 2.0), # floats
    (True, False), # bools
    (None, None), # None
    (object(), object()) # objects
]

@pytest.mark.parametrize("key, value", key_value_test_data)
def test_ChildItem_name(key, value):
    child_item = ChildItem(key, value)

    # the name should be in repr format
    assert child_item.name == f"[{key!r}]"

@pytest.mark.parametrize("key, value", key_value_test_data)
def test_ChildItem_expr(key, value):
    obj_expr = "obj"
    child_item = ChildItem(key, value)

    # the expr should be in repr format
    assert child_item.expr(obj_expr) == f"({obj_expr})[{key!r}]"

sequence_inspector_test_data = [
    [1, 2, 3], # list
    (1, 2, 3), # tuple
    range(1, 4), # range
    "foo", # string
    array.array("i", [1, 2, 3]), # array
    set([1, 2, 3]), # set
    frozenset([1, 2, 3]), # frozenset
    collections.namedtuple("Point", ["x", "y"])(1, 2), # namedtuple
    collections.deque([1, 2, 3]), # deque
    collections.UserList([1, 2, 3]), # UserList
    collections.UserString("foo"), # UserString
    bytes([1, 2, 3]), # bytes
    bytearray([1, 2, 3]), # bytearray
    memoryview(b"foo"), # memoryview
]

@pytest.mark.parametrize("sequence", sequence_inspector_test_data)
def test_SequenceInspector_children(sequence):
    inspector = SequenceInspector(sequence)
    children = list(inspector.children())

    # The children contain the length and the items, so the length should be len(sequence) + 1
    assert len(children) == len(sequence) + 1

    # The first item is the length
    assert isinstance(children[0], ChildLen)
    assert children[0].name == "len()"
    assert children[0].value == len(sequence)

    # The rest of the items are the items in the sequence
    iterator = iter(sequence)
    for i, child in enumerate(children[1:], 0):
        assert isinstance(child, ChildItem)
        assert child.name == f"[{i}]"
        assert child.value == next(iterator)

mapping_inspector_test_data = [
    {"key1": "value1", "key2": "value2"}, # dict
    collections.ChainMap({"key1": "value1"}, {"key2": "value2"}), # ChainMap
    collections.Counter({"key1": 1, "key2": 2}), # Counter
    collections.defaultdict(lambda: "default", {"key1": "value1", "key2": "value2"}), # defaultdict
    collections.OrderedDict({"key1": "value1", "key2": "value2"}), # OrderedDict
    collections.UserDict({"key1": "value1", "key2": "value2"}), # UserDict
]

@pytest.mark.parametrize("mapping", mapping_inspector_test_data)
def test_MappingInspector_children(mapping):
    inspector = MappingInspector(mapping)
    children = list(inspector.children())

    # The children contain the length and the items, so the length should be 1 + len(mapping)
    assert len(children) == 1 + len(mapping)

    # The first item is the length
    assert isinstance(children[0], ChildLen)
    assert children[0].name == "len()"
    assert children[0].value == len(mapping)

    # The rest of the items are the items in the mapping
    for key, child in zip(mapping.keys(), children[1:]):
        assert isinstance(child, ChildItem)
        assert child.name == f"[{key!r}]"
        assert child.value == mapping[key]

def test_ListInspector_repr():
    sequence = [1, 2, 3]
    list_inspector = ListInspector(sequence)
    reprs = list(list_inspector.repr())
    assert len(reprs) == len(sequence)
    for i, repr in enumerate(reprs):
        assert repr == str(sequence[i])
