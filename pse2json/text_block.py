from dataclasses import dataclass


@dataclass
class Rectangle:
    left: float
    top: float
    right: float
    bottom: float

    def __init__(self, left: float, top: float, right: float, bottom: float):
        if (left > right):
            self.left = right
            self.right = left
        else:
            self.left = left
            self.right = right

        if (top > bottom):
            self.top = bottom
            self.bottom = top
        else:
            self.top = top
            self.bottom = bottom

    def in_rectangle(self, rect: 'Rectangle') -> bool:
        return (
            rect.left <= self.left and self.right <= rect.right
            and rect.top <= self.top and self.bottom <= rect.bottom)


@dataclass
class TextBlock:
    rect: Rectangle
    text: str

    def in_rectangle(self, rect: Rectangle) -> bool:
        return self.rect.in_rectangle(rect)
