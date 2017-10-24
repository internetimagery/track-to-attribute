# Redesign.
#
# Load file prompt directly when opening the gui.
# No need to check for file existance or updates etc.


# add as many attributes as wanted in order to work on them at once.
# button "new" create a new entry.
# entry: [x/y/angle] [track] [stabalize/angle] [remove]

import maya.cmds as cmds
import logic

NONE = "---"


def get_attribute():
    """ Get selected attribute from channelbox """
    return set(["{}.{}".format(o, at) for o in cmds.ls(sl=True) for at in cmds.channelBox("mainChannelBox", sma=True, q=True) or [] if cmds.attributeQuery(at, n=o, ex=True)])

def browse():
    """ Open file browser """
    path = cmds.fileDialog2(
        fm=1,
        ff="Tracker file (*.nk *.ntp)",
        dir=logic.real_path(cmds.textFieldButtonGrp(s.nuke, q=True, tx=True)))
    if path:
        s.load_tracker(path[0])

class Attribute(object):
    """ Attribute gui entry """
    def __init__(s, parent, attr, trackers):
        s._active = True
        s._attr = cmds.textField(w=400, tx=attr, p=parent)
        s._axis = cmds.optionMenu(p=parent)
        for t in ["X", "Y", "Angle"]:
            cmds.menuItem(l=t, p=s._axis)
        s._track1 = cmds.optionMenu(p=parent)
        for t in trackers:
            cmds.menuItem(l=t, p=s._track1)
        s._track2 = cmds.optionMenu(p=parent)
        for t in trackers:
            cmds.menuItem(l=t, p=s._track2)
        s._key = cmds.button(l="Key", c=s.delete, bgc=(0.2, 0.5, 0.4), p=parent)
        s._del = cmds.button(l="Remove", c=s.delete, bgc=(0.4, 0.3, 0.3), p=parent)
    def key(s, func=None):
        """ Key attr data """
        if s._active:
            return (s.attr, s.axis, s.track1, s.track2)
    def delete(s, *_):
        """ Remove UI element """
        if s._active:
            cmds.deleteUI([s._attr, s._axis, s._track1, s._track2, s._key, s._del])
            s._active = False
    attr = property(
        (lambda s:cmds.textField(s._attr, q=True, tx=True)),
        (lambda s, x:cmds.textField(s._attr, e=True, tx=x)))
    axis = property(lambda s:cmds.optionMenu(s._axis, q=True, v=True))
    track1 = property(lambda s:cmds.optionMenu(s._track1, q=True, v=True))
    track2 = property(lambda s:cmds.optionMenu(s._track2, q=True, v=True))

class Window(object):
    def __init__(s):
        """ Apply tracker data to attributes """
        # Get tracker file
        path = cmds.fileDialog2(fm=1, ff="Tracker file (*.nk *.ntp)")
        if path:
            path = path[0]

            # Load trackers
            s.data = logic.get_tracks(path)
            if not s.data:
                raise RuntimeError("No tracking data found.")

            # Prep data
            s.trackers = [NONE] + s.data.keys()
            s.attributes = []

            # Open window
            win = cmds.window(t=path)
            main = cmds.columnLayout(adj=True)
            cmds.button(l="Add from Channel Box", bgc=(0.2, 0.5, 0.4), c=s.add_attr)
            s.root = cmds.rowColumnLayout(nc=6)
            cmds.text(l="Attribute")
            cmds.text(l="Axis")
            cmds.text(l="Tracker")
            cmds.text(l="Stabalize / Angle")
            cmds.button(l="Key All")
            cmds.button(l="Clear all", c=s.clear_all)
            for i in range(3):
                s.attributes.append(Attribute(s.root, "Attr! %s" % i, s.trackers))
            cmds.showWindow()

    def clear_all(s, *_):
        """ Remove all attrs """
        for at in s.attributes:
            at.delete()
        s.attributes = []

    def key_all(s, *_):
        """ Key all """
        result = [(at.attr, at.axis, at.track1, at.track2)for at in s.attributes]

    def add_attr(s, *_):
        """ Add new attribute from channelbox """
        attrs = get_attribute()
        for at in attrs:
            s.attributes.append(Attribute(s.root, at, s.trackers))
