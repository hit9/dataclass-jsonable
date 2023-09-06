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
class S1(J):
    data: "Dict[str, Any]"
    n: "Optional[int]"


def test_forward_ref_generics():
    s = S1(data={"x": 1}, n=2)
    assert s.json() == {"data": {"x": 1}, "n": 2}
    s1 = S1.from_json({"data": {"x": 1}, "n": 2})
    assert s1 == s


@dataclass
class S2(J):
    x: list["int"]


def test_forward_ref_generics_py310_issue41370_1():
    s = S2(x=[1, 2, 3])
    assert s.json() == {"x": [1, 2, 3]}
    d = S2.from_json({"x": [1, 2, 3]})
    assert d == s


@dataclass
class S3(J):
    x: list["Node"]


def test_forward_ref_generics_py310_issue41370_2():
    s = S3(x=[Node(data=1)])
    assert s.json() == {"x": [{"data": 1, "children": []}]}
    d = S3.from_json({"x": [{"data": 1, "children": []}]})
    assert d == s


@dataclass
class S4(J):
    d: dict["str", list["Node"]]


def test_forward_ref_generics_py310_issue41370_3():
    s = S4(d={"k1": [Node(data=2, children=[Node(data=3)])]})
    assert s.json() == {
        "d": {"k1": [{"data": 2, "children": [{"data": 3, "children": []}]}]}
    }
    d = s.json()
    s1 = S4.from_json(d)
    assert s1 == s
