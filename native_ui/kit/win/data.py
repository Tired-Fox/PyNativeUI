from __future__ import annotations
from typing import Iterator
from functools import cached_property

class Rect:
    def __init__(self, left: int, top: int, right: int, bottom: int):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    @cached_property
    def normalized(self) -> Rect:
        return Rect(0, 0, self.right - self.left, self.bottom - self.top)

    @cached_property
    def width(self) -> int:
        return self.right - self.left

    @cached_property
    def height(self) -> int:
        return self.bottom - self.top

    def update(self, rect: Rect):
        self.left = rect.left
        self.top = rect.top
        self.right = rect.right
        self.bottom = rect.bottom

    def __iter__(self) -> Iterator[int]:
        yield self.left
        yield self.top
        yield self.right
        yield self.bottom

    def __repr__(self) -> str:
        return f"({self.left}, {self.top}, {self.right}, {self.bottom})"

