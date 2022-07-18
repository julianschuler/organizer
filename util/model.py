"""Simplified model required for converting DB to JSON files"""


class Element:
    """Base class for all elements containing subelements"""

    def __init__(self, subelems):
        self.subelems = subelems


class Box(Element):
    """Box, contains drawers"""

    def __init__(self, drawers, x, y, w, h):
        super().__init__(drawers)
        self.x = x
        self.y = y
        self.w = w
        self.h = h


class Drawer(Element):
    """Drawer, can countain multiple Items"""

    def __init__(self, items=[]):
        super().__init__(items)


class Item:
    """Item, has a name and can have an amount"""

    def __init__(self, name, amount=None):
        self.name = name
        self.amount = amount
        self.lower = self.name.lower()
