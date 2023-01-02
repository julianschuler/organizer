#!/usr/bin/env python3

from pyglet import app
from pyglet.graphics import Batch, Group

from gui import Groups, OrganizerGUI, OrganizerWindow
from model import Organizer

if __name__ == "__main__":
    # setup batch and groups
    batch = Batch()
    groups = Groups()
    # create window
    window = OrganizerWindow(batch, groups)
    # create organizer object
    organizer = Organizer.load()
    organizer_gui = OrganizerGUI(organizer, batch, groups)
    # set organizer for window and execute main program loop
    window.set_organizer(organizer_gui)
    app.run()
    # save organizer at program exit
    organizer.save()
