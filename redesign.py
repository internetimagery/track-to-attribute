# Redesign.
#
# Load file prompt directly when opening the gui.
# No need to check for file existance or updates etc.


# add as many attributes as wanted in order to work on them at once.
# button "new" create a new entry.
# entry: [x/y/angle] [track] [stabalize/angle] [remove]

import maya.cmds as cmds

NONE = "---"


def get_attribute():
    """ Get selected attribute from channelbox """
    for obj in cmds.ls(sl=True) or []:
        for attr in cmds.channelBox("mainChannelBox", sma=True, q=True) or []:
            if cmds.attributeQuery(attr, n=obj, ex=True):
                return "{}.{}".format(obj, attr)
    return ""


class Attribute(object):
    """ Attribute gui entry """
    def __init__(s, parent, attr="", trackers=[]):
        s.active = True
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
        s._del = cmds.button(l="Remove", c=s.delete, bgc=(0.4, 0.3, 0.3), p=parent)
    def delete(s, *_):
        """ Remove UI element """
        if s.active:
            cmds.deleteUI([s._attr, s._axis, s._track1, s._track2, s._del])
            s.active = False
    attr = property(
        (lambda s:cmds.textField(s._attr, q=True, tx=True)),
        (lambda s, x:cmds.textField(s._attr, e=True, tx=x)))
    axis = property(lambda s:cmds.optionMenu(s._axis, q=True, v=True))
    track1 = property(lambda s:cmds.optionMenu(s._track1, q=True, v=True))
    track2 = property(lambda s:cmds.optionMenu(s._track2, q=True, v=True))

class Window(object):
    def __init__(s):
        """ Apply tracker data to attributes """
        s.trackers = [NONE, "one", "two", "three!"]
        s.attributes = []
        win = cmds.window(rtf=True)
        main = cmds.columnLayout(adj=True)
        cmds.button(l="Add Attribute", c=s.add_attr)
        cmds.scrollLayout(cr=True, h=300)
        s.root = cmds.rowColumnLayout(nc=5)
        cmds.text(l="Attribute")
        cmds.text(l="Axis")
        cmds.text(l="Tracker")
        cmds.text(l="Stabalize / Angle")
        cmds.button(l="Clear all", c=s.clear_all)
        for i in range(3):
            s.attributes.append(Attribute(s.root, "Attr! %s" % i, s.trackers))
        cmds.setParent(main)
        cmds.separator()
        cmds.button(l="Keyframe")
        cmds.showWindow()

    def clear_all(s, *_):
        """ Remove all attrs """
        for at in s.attributes:
            at.delete()
        s.attributes = []

    def add_attr(s, *_):
        """ Add new attribute from channelbox """
        s.attributes.append(Attribute(s.root, get_attribute(), s.trackers))
