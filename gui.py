from pyglet import event
from pyglet.gl import glClearColor, GL_TRIANGLES
from pyglet.window import key, Window
from pyglet.shapes import Rectangle
from pyglet.text import Label, caret
from pyglet.text.document import FormattedDocument
from pyglet.text.layout import IncrementalTextLayout, ScrollableTextLayout
from settings import *
import model



class OrganizerWindow(Window):
    """Main program window, handles the background color an resizing"""
    def __init__(self, organizer, batch, groups):
        if FULLSCREEN:
            super().__init__(caption=WINDOW_TITLE, fullscreen=True)
        else:
            super().__init__(
                WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, resizable=True)
        glClearColor(
            BACKGROUND_COLOR[0]/255, BACKGROUND_COLOR[1]/255, 
            BACKGROUND_COLOR[2]/255, 1)
        self.organizer = organizer
        # define callbacks used by caret in text input
        def click_callback(x, y): self.on_click(x, y)
        def enter_callback(): self.on_enter()
        def motion_callback(motion): self.on_motion(motion)
        def find_callback(text): self.on_search(text)
        # create text input and item list
        self.text_input = TextInput(
            batch, groups, click_callback, 
            enter_callback, motion_callback, find_callback)
        self.item_list = ItemList(self.text_input.font_height, batch, groups)
        # initialize member variables
        self.batch = batch
        self.prev_w = 0
        self.prev_h = 0
        self.selected_drawer = None
        self.found = []
        self.text = ''

    def on_draw(self):
        """Window content needs to be redrawn, resize contents if necassary"""
        self.clear()
        if (self.width != self.prev_w or self.height != self.prev_h):
            self.prev_w = self.width
            self.prev_h = self.height
            self.organizer.resize(
                self.prev_w, self.prev_h, self.text_input, self.item_list)
        self.batch.draw()
        self.push_handlers(self.text_input.caret)

    def on_click(self, x, y):
        """Mouse has been clicked at given coordinate, (de-)select drawer"""
        drawer = self.organizer.get_drawer(x, y)
        if (drawer is not self.selected_drawer):
            self.clear_all()
            if (self.selected_drawer is not None):
                self.selected_drawer.highlight()
            else:
                self.text_input.clear_text()
            if (drawer is not None):
                drawer.highlight(SELECT_MASK)
                items = drawer.get_items()
            else:
                items = []
                self.text_input.clear_text()
            self.item_list.set_items(items)
            self.selected_drawer = drawer

    def on_enter(self):
        """Enter has been pressed, handle adding items"""
        name = self.text_input.get_text().strip()
        self.text_input.clear_text()
        self.clear_all()
        if (name != ''):
            items = []
            if (self.selected_drawer is not None):
                self.selected_drawer.add_item(name)
                items = self.selected_drawer.get_items()
            self.item_list.set_items(items)

    def on_key_press(self, key, mod):
        """Has no function, supresses closing window via ESC"""
        pass

    def on_motion(self, motion):
        """Handle motion input like up, down and delete"""
        selected = self.item_list.get_selected()
        if (motion == key.MOTION_DOWN):
            self.item_list.select(selected + 1)
        elif (motion == key.MOTION_UP):
            self.item_list.select(selected - 1)
        elif (motion == key.MOTION_DELETE):
            if (selected != -1 and self.selected_drawer is not None):
                del self.selected_drawer.get_items()[selected]
                items = self.selected_drawer.get_items()
                self.item_list.set_items(items)
                self.item_list.select()
        if (self.selected_drawer is None):
            new_selected = self.item_list.get_selected()
            if (selected != new_selected):
                if (selected >= 0):
                    self.item_drawers[selected].highlight(HIGHLIGHT_MASK)
                if (new_selected >= 0):
                    self.item_drawers[new_selected].highlight(SELECT_MASK)

    def on_search(self, text):
        """Handle the saerch of the organizer for items"""
        if self.selected_drawer is None:
            if (self.text != text):
                self.text = text
                self.clear_all()
                items = []
                self.item_drawers = []
                if (len(text.strip()) >= FIND_MIN_LENGTH):
                    self.found = self.organizer.find(text.lower().split())
                    for drawer, i in self.found:
                        drawer.highlight(HIGHLIGHT_MASK)
                        items += i
                        self.item_drawers += [drawer] * len(i)
                self.item_list.set_items(items)

    def clear_all(self):
        """Clear all selections and highlights"""
        for drawer, items in self.found:
            drawer.highlight()
        self.found = []
        self.item_list.select()


class OrganizerGUI(model.Element):
    """Class of organizer objects with resizeable GUI"""
    def __init__(self, organizer, batch, groups):
        # draw organizer background
        self.rect = Rectangle(
            0, 0, 100, 100, color=BOX_COLOR, batch=batch, group=groups[0])
        # create list of BoxGUI objects from boxes
        boxes_gui = []
        for box in organizer.subelems:
            boxes_gui.append(BoxGUI(
                box.subelems, box.x, box.y, box.w, box.h, batch, groups))
        # intialize parent class with newly created drawers_gui
        super().__init__(boxes_gui)
        self.w = organizer.w
        self.h = organizer.h

    def resize(self, window_w, window_h, text_input, item_list):
        """Resize the organizer and its subelements to a given window size"""
        try:
            # check width to height ratio
            if (window_w / window_h >= self.w / self.h):
                # scale organizer to fill height
                self.rect.height = window_h * (1 - 2 * WINDOW_MARGIN)
                self.rect.width = self.rect.height * self.w / self.h
                self.rect.x = self.rect.y = window_h * WINDOW_MARGIN
                # calulate text input position and width
                text_x = self.rect.width + 2 * self.rect.x
                text_y = (window_h * (1 - WINDOW_MARGIN) 
                    - text_input.rect.height)
                text_w = max(0, window_w - text_x - self.rect.x)
                list_y = text_y - window_h * LIST_OFFSET
            else:
                # scale organizer to fill width
                self.rect.width = text_w = window_w * (1 - 2 * WINDOW_MARGIN)
                self.rect.height = self.rect.width * self.h / self.w
                self.rect.x = text_x = window_w * WINDOW_MARGIN
                self.rect.y = window_h - self.rect.height - self.rect.x
                text_y = (window_h - self.rect.height - 2 * text_x 
                    - text_input.rect.height)
                list_y = text_y - window_w * LIST_OFFSET
            list_h = max(0, list_y - window_h * WINDOW_MARGIN)
            # resize text input
            text_input.resize(text_x, text_y, text_w)
            item_list.resize(text_x, list_y, text_w, list_h)
            # resize all subelements as well
            block_size = self.rect.width / self.w
            bm = block_size * BOX_MARGIN
            dm = block_size * DRAWER_MARGIN
            hh = block_size * HANDLE_HEIGHT
            ht = block_size * HANDLE_THICKNESS
            for box in self.subelems:
                box_x = box.x * block_size + self.rect.x
                box_y = box.y * block_size + self.rect.y
                box_w = box.w * block_size
                box_h = box.h * block_size
                box.resize(box_x, box_y, box_w, box_h, bm, dm, hh, ht)
        except ZeroDivisionError:
            pass

    def get_drawer(self, x, y):
        """Return the drawer corresponding to a given coordinate"""
        for box in self.subelems:
            for drawer in box.subelems:
                if (drawer.is_clicked(x, y)):
                    return drawer
        return None


class BoxGUI(model.Element):
    """Class of box objects with resizeable GUI""" 
    def __init__(self, drawers, x, y, w, h, batch, groups):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        # create list of DrawerGUI objects from drawers
        drawers_gui = []
        for drawer in drawers:
            drawers_gui.append(DrawerGUI(drawer.subelems, batch, groups))
        # intialize parent class with newly created drawers_gui
        super().__init__(drawers_gui)

    def resize(self, x, y, w, h, bm, dm, hh, ht):
        """Resize the box and its subelements to a given pixel size"""
        # calcultate drawer parameters
        drawer_num = len(self.subelems)
        module_h = (h - 2 * bm) / drawer_num
        drawer_w = w - 2 * (bm + dm)
        drawer_h = module_h - 2 * dm
        drawer_x = x + bm + dm
        module_y = y + bm + dm
        # create list of DrawerGUI objects from drawers
        for i,drawer in enumerate(self.subelems):
            drawer_y = module_y + (drawer_num - 1 - i) * module_h
            drawer.resize(drawer_x, drawer_y, drawer_w, drawer_h, hh, ht)


class DrawerGUI(model.Element):
    """Class of drawer objects with resizeable GUI"""
    def __init__(self, items, batch, groups):
        super().__init__(items)
        self.rect = Rectangle(
            0, 0, 1, 1, color=DRAWER_COLOR, batch=batch, group=groups[1])
        self.handle = batch.add(
            TRIANGLE_COUNT * 3, GL_TRIANGLES, groups[2], 'v2f', 'c3B')
        self.handle.colors = HANDLE_COLOR * TRIANGLE_COUNT * 3

    def is_clicked(self, x, y):
        """Test if drawer is clicked"""
        return (x >= self.rect.x and x <= self.rect.x + self.rect.width
            and y >= self.rect.y and y <= self.rect.y + self.rect.height)

    def resize(self, x, y, w, h, hh, ht):
        """Resize the drawer to a given pixel size"""
        self.rect.x = x
        self.rect.y = y
        self.rect.height = h
        self.rect.width = w
        hw = w * HANDLE_WIDTH
        ox = x + (w - hw) / 2
        hhy = hh
        self.handle.vertices = [
            ox, y,              ox + hh, y,         ox + hh, y - hhy,
            ox + hh, y - hhy,   ox + hh, y,         ox + hw - hh, y,
            ox + hh, y - hhy,   ox + hw - hh, y,    ox + hw - hh, y - hhy,
            ox + hw, y,         ox + hw - hh, y,    ox + hw - hh, y - hhy,
            ox, y,              ox, y + ht,         ox + hw, y,
            ox + hw, y,         ox, y + ht,         ox + hw, y + ht]

    def highlight(self, color_mask=(0, 0, 0)):
        """Highlight the drawer with a given color mask, remove highlighting 
        if no input is given"""
        color_rect = []
        color_handle = []
        for i, c in enumerate(color_mask):
            color_rect.append(DRAWER_COLOR[i] + c)
            color_handle.append(HANDLE_COLOR[i] + c)
        self.rect.color = color_rect
        self.handle.colors = color_handle * TRIANGLE_COUNT * 3

    def add_item(self, name, amount=None):
        """Add an item to the drawer"""
        self.subelems.append(model.Item(name, amount))

    def get_items(self):
        """Return all items of the drawer"""
        return self.subelems

    def find(self, str):
        """Return all items containting str together with the drawer"""
        items = []
        for item in self.subelems:
            items += item.find(str)
        if (items != []):
            return [(self, items)]
        return []


class TextInput:
    """Text input field"""
    def __init__(self, batch, groups, 
            on_click, on_enter, on_motion, on_search):
        # create document 
        self.document = FormattedDocument(' ') 
        self.document.set_style(
            0, 1, dict(font_name=FONT_NAME, 
            font_size=FONT_SIZE, color=FONT_COLOR))
        # calculate font height and margin
        font = self.document.get_font(0)
        self.font_height = font.ascent - font.descent
        self.margin = self.font_height * TEXT_INPUT_MARGIN
        # create text input
        self.input = IncrementalTextLayout(
            self.document, 100, self.font_height, batch=batch, group=groups[1])
        self.input.x = 100
        self.input.y = 100
        # creating a caret and push it to window handlers 
        self.caret = Caret(
            self.input, FONT_COLOR[:3], 
            on_click, on_enter, on_motion, on_search)
        self.clear_text()
        # create background rectangle
        self.rect = Rectangle(
            0, 0, 100, self.font_height + 2 * self.margin, 
            color=TEXT_INPUT_COLOR, batch=batch, group=groups[0])

    def resize(self, x, y, w):
        """Resize the text input with given coordinates and width"""
        self.rect.x = x
        self.rect.y = y
        self.rect.width = w
        self.input.x = x + self.margin
        self.input.y = y + self.margin
        self.input.width = w - 2 * self.margin

    def get_text(self):
        """Return currently displayed text"""
        return self.document.text

    def clear_text(self):
        """Clear displayed text"""
        self.document.text = ''


class ItemList:
    """List of items below the text input field drawn to available space"""
    def __init__(self, font_height, batch, groups):
        self.font_height = font_height
        self.margin = font_height * TEXT_INPUT_MARGIN
        self.line_height = self.font_height + 2 * self.margin
        # create document
        self.text_box = Label(
            '', FONT_NAME, FONT_SIZE, width=1, 
            multiline=True, anchor_y = 'top', color=ITEM_FONT_COLOR, 
            batch=batch, group=groups[2])
        # create background rectangle
        self.rect = Rectangle(
            0, 0, 100, self.line_height, 
            color=ITEM_LIST_COLOR, batch=batch, group=groups[0])
        # create select rectangle
        self.select_rect = Rectangle(
            0, 0, 100, self.line_height,
            color=ITEM_SELECT_COLOR, batch=batch, group=groups[1])
        self.select_rect.visible = False
        # initialze member variables
        self.lines = 0
        self.select_num = 0
        self.items = []
        self.max_h = 1
        self.y = 0

    def resize(self, x, y, w, max_h):
        """Resize the list content to given coordinates, width and 
        maximum height"""
        self.y = y
        self.max_h = max_h
        self.__update()
        self.rect.x = x
        self.rect.width = w
        self.select_rect.x = x
        self.select_rect.width = w
        self.text_box.x = x + self.margin
        self.text_box.y = y - self.margin
        self.text_box.width = w - 2 * self.margin

    def select(self, num=-1):
        """Select an item via list index"""
        if (num < 0):
            self.select_rect.visible = False
            self.__update()
        elif (num < self.lines):
            self.select_rect.visible = True
            self.select_num = num
            self.__update()

    def get_selected(self):
        """Return index of the selected item, -1 if no item is selected"""
        if (self.select_rect.visible):
            return self.select_num
        return -1

    def set_items(self, items=[]):
        """Set list content to a given list of items"""
        self.items = [i.name for i in items]
        self.__update()

    def __update(self):
        """Update size and list elements"""
        self.lines = min(len(self.items), int(self.max_h // self.line_height))
        h = self.line_height * self.lines
        self.rect.height = h
        self.rect.y = self.y - h
        self.select_rect.y = self.y - self.line_height * (1 + self.select_num)
        self.text_box.text = ('\n\n').join(self.items[:self.lines])


class Caret(caret.Caret):
    """Custom caret to handle specific events with callbacks"""
    def __init__(self, input, color, on_click, on_enter, on_motion, on_search):
        super().__init__(input, color=color)
        self.prev_x = 0
        self.prev_y = 0
        self.document = input.document
        self.on_click = on_click
        self.on_enter = on_enter
        self.on_motion = on_motion
        self.on_search = on_search

    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse press"""
        if (x != self.prev_x and y != self.prev_y):
            self.prev_x = x
            self.prev_y = y
            self.on_click(x, y)

    def on_text(self, text):
        """Handle text input by detecting enter/return events"""
        if (text == CHAR_ENTER):
            self.on_enter()
        else:
            super().on_text(text)
            self.on_search(self.document.text)
        return event.EVENT_HANDLED

    def on_text_motion(self, motion, select=False):
        """Handle motion input events"""
        super().on_text_motion(motion, select)
        self.on_motion(motion)
        self.on_search(self.document.text)
        return event.EVENT_HANDLED
