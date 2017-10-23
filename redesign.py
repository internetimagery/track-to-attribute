# Redesign.
#
# Load file prompt directly when opening the gui.
# No need to check for file existance or updates etc.


# add as many attributes as wanted in order to work on them at once.
# button "new" create a new entry.
# entry: [x/y/angle] [track] [stabalize/angle] [remove]

import maya.cmds as cmds

class Attribute(object):
    """ Attribute gui entry """
    def __init__(s, parent, trackers=[]):
        s._root = cmds.rowLayout(nc=5, p=parent)
        s._attr = cmds.textField(p=s._root)
        s._axis = cmds.optionMenu(p=s._root)
        for t in ["X", "Y", "Angle"]:
            cmds.menuItem(l=t, p=s._axis)
        s._track1 = cmds.optionMenu(p=s._root)
        for t in trackers:
            cmds.menuItem(l=t, p=s._track1)
        s._track2 = cmds.optionMenu(p=s._root)
        for t in trackers:
            cmds.menuItem(l=t, p=s._track2)
        s._del = cmds.button(l="Remove", c=s._delete, p=s._root)
    def _delete(s, *_):
        """ Remove UI element """
        cmds.deleteUI(s._root)
    active = property(lambda s:cmds.layout(s._root, ex=True))
    attr = property(
        (lambda s:cmds.textField(s._attr, q=True, tx=True)),
        (lambda s, x:cmds.textField(s._attr, e=True, tx=x)))
    axis = property(lambda s:cmds.optionMenu(s._axis, q=True, v=True))
    track1 = property(lambda s:cmds.optionMenu(s._track1, q=True, v=True))
    track2 = property(lambda s:cmds.optionMenu(s._track2, q=True, v=True))

class Window(object):
    def __init__(s):
        """ Apply tracker data to attributes """
        s.trackers = ["one", "two", "three!"]
        attriutes = []
        win = cmds.window(rtf=True)
        main = cmds.columnLayout(adj=True)
        cmds.button(l="Add Attribute", c=s.add_attr)
        s.root = cmds.scrollLayout(cr=True, h=300)

        for i in range(3):
            at = (Attribute(s.root, s.trackers))
            at.attr = "Attr! %s" % i
        cmds.setParent(main)
        cmds.separator()
        cmds.button(l="Keyframe")
        cmds.showWindow()

    def add_attr(s, *_):
        """ Add new attribute from channelbox """
        at = Attribute(s.root, s.trackers)
        at.attr = "NEW ATTR"
