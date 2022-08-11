from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from dataclass_jsonable import J, json_options


@dataclass
class Tree(J):
    __default_json_options__ = json_options(omitempty=True)
    name: str
    left: Optional["Tree"] = None
    right: Optional["Tree"] = None


def test_forward_ref_tree():
    tree = Tree("root", left=Tree("left"), right=Tree("right"))
    d = {"name": "root", "left": {"name": "left"}, "right": {"name": "right"}}
    assert tree.json() == d
    Tree.from_json(d) == tree


@dataclass
class Node(J):
    data: int
    children: List["Node"] = field(default_factory=list)


def test_forward_ref_node():
    node = Node(1, children=[Node(2), Node(3), Node(4, children=[Node(5)])])
    d = {
        "data": 1,
        "children": [
            {"data": 2, "children": []},
            {"data": 3, "children": []},
            {"data": 4, "children": [{"data": 5, "children": []}]},
        ],
    }
    assert node.json() == d


@dataclass
class Simple(J):
    data: "Dict[str, Any]"
    n: "Optional[int]"


def test_forward_ref_generics():
    s = Simple(data={"x": 1}, n=2)
    assert s.json() == {"data": {"x": 1}, "n": 2}
    s1 = Simple.from_json({"data": {"x": 1}, "n": 2})
    assert s1 == s
