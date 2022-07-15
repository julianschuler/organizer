from pyglet import app
from pyglet.graphics import Batch, OrderedGroup
from gui import OrganizerGUI, OrganizerWindow
from model import Organizer
from settings import GROUP_COUNT


if __name__ == "__main__":
    # setup batch and groups
    batch = Batch()
    groups = [OrderedGroup(i) for i in range(GROUP_COUNT)]
    # create organizer object
    organizer = Organizer()
    organizer_gui = OrganizerGUI(organizer, batch, groups)
    # create window and execute main program loop
    window = OrganizerWindow(organizer_gui, batch, groups)
    app.run()
    # save organizer at program exit
    organizer.save()
