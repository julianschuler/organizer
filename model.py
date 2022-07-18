import json
import settings as conf


class Element:
    """Base class for all elements containing subelements"""

    subelem_name = ""

    def __init__(self, subelems):
        self.subelems = subelems

    def find(self, str):
        """Return all lowest level elements containing str"""
        result = []
        for subelem in self.subelems:
            result += subelem.find(str)
        return result

    def asdict(self):
        subelems = []
        for subelem in self.subelems:
            subelems.append(subelem.asdict())
        return {self.subelem_name: subelems}


class Organizer(Element):
    """Organizer, contains boxes"""

    subelem_name = "boxes"

    def __init__(self, boxes, width, height):
        super().__init__(boxes)
        self.w = width
        self.h = height

    def save(self):
        """Save the organizer and its content to disk"""
        with open(conf.ORGANIZER_JSON, "w") as f:
            json.dump(self.asdict(), f, indent=conf.ORGANIZER_JSON_INDENT)

    def asdict(self):
        dct = {"width": self.w, "height": self.h}
        dct.update(super().asdict())
        return dct

    @classmethod
    def fromdict(cls, dct):
        boxes = []
        for box in dct[cls.subelem_name]:
            boxes.append(Box.fromdict(box))
        return Organizer(boxes, dct["width"], dct["height"])

    @classmethod
    def load(cls):
        """Load the organizer and its content from disk"""
        try:
            with open(conf.ORGANIZER_JSON) as f:
                dct = json.load(f)
            organizer = Organizer.fromdict(dct)
        except FileNotFoundError:
            organizer = cls.__parse_config()
        return organizer

    @classmethod
    def __parse_config(cls):
        """Parse the organizer structure from config file"""
        boxes = []
        w = 0
        h = 0
        symbols = {}
        layout = []
        # read conf file
        with open(conf.ORGANIZER_CONF) as conf_file:
            lines = conf_file.read().splitlines()
        # parse drawer count and box layout to symbol dict and layout array
        for line in lines:
            if len(line) > 2 and line[0] != "#":
                if ":" in line:
                    s = line.split(":")
                    symbols[s[0]] = s[1]
                else:
                    layout.append(line.split(" "))
                    w = max(w, len(layout[-1]))
                    h += 1
        # create boxes from layout
        org_w = len(layout[0])
        org_h = len(layout)
        for i, line in enumerate(layout):
            j = 0
            while j < org_w:
                s = c = line[j]
                if c == "":
                    j += 1
                else:
                    w = 0
                    h = 0
                    x = j
                    # create correct amount of drawers depending on symbol
                    drawers = []
                    for k in range(int(symbols[s])):
                        drawers.append(Drawer([]))
                    # determine box width
                    while c == s and j < org_w:
                        j += 1
                        w += 1
                        if j < org_w:
                            c = line[j]
                    # determine box height and flag array entries to be ignored
                    c = s
                    while c == s and i + h < org_h:
                        for k in range(w):
                            layout[i + h][x + k] = ""
                        h += 1
                        if i + h < org_h:
                            c = layout[i + h][x]
                    boxes.append(Box(drawers, x, org_h - i - h, w, h))
        return Organizer(boxes, org_w, org_h)


class Box(Element):
    """Box, contains drawers"""

    subelem_name = "drawers"

    def __init__(self, drawers, x, y, w, h):
        super().__init__(drawers)
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def asdict(self):
        dct = {"x": self.x, "y": self.y, "w": self.w, "h": self.h}
        dct.update(super().asdict())
        return dct

    @classmethod
    def fromdict(cls, dct):
        drawers = []
        for drawer in dct[cls.subelem_name]:
            drawers.append(Drawer.fromdict(drawer))
        return Box(drawers, dct["x"], dct["y"], dct["w"], dct["h"])


class Drawer(Element):
    """Drawer, can countain multiple Items"""

    subelem_name = "items"

    def __init__(self, items=[]):
        super().__init__(items)

    @classmethod
    def fromdict(cls, dct):
        items = []
        for item in dct[cls.subelem_name]:
            items.append(Item.fromdict(item))
        return Drawer(items)


class Item:
    """Item, has a name and can have an amount"""

    def __init__(self, name, amount=None):
        self.name = name
        self.amount = amount
        self.lower = self.name.lower()

    def find(self, str):
        """Return [self] if all elems of str is contained in name, else []"""
        for s in str:
            if s not in self.lower:
                return []
        return [self]

    def asdict(self):
        return {"name": self.name, "amount": self.amount}

    @classmethod
    def fromdict(cls, dct):
        return Item(dct["name"], dct["amount"])
