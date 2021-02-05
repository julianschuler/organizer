### general settings
# char produced by enter/return at on_text event, possibly OS spcific
CHAR_ENTER = '\r'
FIND_MIN_LENGTH = 3


### GUI settings
#window settings
FULLSCREEN = False
WINDOW_WIDTH = 1920 * 4 // 2
WINDOW_HEIGHT = 1080 * 4 // 2
WINDOW_TITLE = 'Organizer'
FONT_NAME = 'Arial'
FONT_SIZE = 35

# margin size, as fraction of font size
TEXT_INPUT_MARGIN = 0.5
# margin and offset sizes, as fraction of the window
WINDOW_MARGIN = 0.05
LIST_OFFSET = 0.01
# margin sizes, as fraction of a 1x1 box
BOX_MARGIN = 0.03
DRAWER_MARGIN = 0.015
# handle width as fraction of the drawer width
HANDLE_WIDTH = 0.3
# handle height and thickness as fraction of a 1x1 box
HANDLE_HEIGHT = 0.05
HANDLE_THICKNESS = 0.03

# colors
FONT_COLOR = (255, 255, 255, 255)
ITEM_FONT_COLOR = (0, 0, 0, 255)
TEXT_INPUT_COLOR = (15, 15, 15)
ITEM_LIST_COLOR = (180, 180, 180)
ITEM_SELECT_COLOR = (150, 150, 150)
BACKGROUND_COLOR = (50, 50, 50)
BOX_COLOR = (15, 15, 15)
DRAWER_COLOR = (130, 130, 130)
HANDLE_COLOR = [90, 90, 90]
HIGHLIGHT_MASK = (0, 100, 0)
SELECT_MASK = (0, 50, 100)


### data storage settings
# name of the database file
ORGANIZER_DB = 'organizer.db'
# name of the file for the initial config
ORGANIZER_CONF = 'organizer.conf'


### advanced settings, shouldn't be changed
# group count, change only if more groups are needed
GROUP_COUNT = 3
# amount of triangles for displaying the handle
TRIANGLE_COUNT = 6
