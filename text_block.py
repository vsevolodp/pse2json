from dataclasses import dataclass


@dataclass
class Rectangle:
    left: float
    top: float
    right: float
    bottom: float

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
