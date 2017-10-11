# Let thee control the stuff!
import maya.cmds as cmds
import logic
import os

NONE = "---"

def real_path(path):
    """ Get closest real path up the tree """
    while True:
        new_path = os.path.dirname(path)
        if new_path == path:
            return ""
        elif os.path.isdir(new_path):
            return new_path

class Window(object):
    def __init__(s):
        s.data = {}
        s.win = cmds.window("Tracker to Attribute")
        col = cmds.columnLayout(adj=True)
        s.nuke = cmds.textFieldButtonGrp(l="Nuke File:", bl="Browse", adj=2, bc=s.browse, cc=s.load_nuke)
        s.tracker = cmds.optionMenuGrp(l="Tracker:", adj=2) + "|OptionMenu"
        # cmds.menuItem(l=NONE, p=s.tracker)
        s.stabalize = cmds.optionMenuGrp(l="Stabalize:", adj=2) + "|OptionMenu"
        # cmds.menuItem(l=NONE, p=s.stabalize)
        s.outX = cmds.textFieldButtonGrp(l="Output X:", bl="<< CB", adj=2, bc=lambda:s.get_attr(s.outX))
        s.outY = cmds.textFieldButtonGrp(l="Output Y:", bl="<< CB", adj=2, bc=lambda:s.get_attr(s.outY))
        s.scale = cmds.intFieldGrp(l="Scale X / Y:", v1=1, v2=1, nf=2)
        s.go = cmds.button(l="Keyframe!", en=False, c=s.run)
        cmds.showWindow()

    def browse(s):
        """ Open file browser """
        path = cmds.fileDialog2(
            fm=1,
            ff="Nuke files (*.nk)",
            dir=real_path(cmds.textFieldButtonGrp(s.nuke, q=True, tx=True)))
        if path:
            s.load_nuke(path[0])

    def load_nuke(s, path):
        """ Load nuke file """
        # Clear out any existing tracks.
        path = path.strip()
        remove = cmds.optionMenu(s.tracker, q=True, ill=True) or []
        remove += cmds.optionMenu(s.stabalize, q=True, ill=True) or []
        if remove:
            cmds.deleteUI(remove)

        if path:

            s.data = logic.get_tracks(path)
            cmds.textFieldButtonGrp(s.nuke, e=True, tx=path)

            # Add current tracks.
            cmds.menuItem(l=NONE, p=s.stabalize)
            for track in s.data:
                cmds.menuItem(l=track, p=s.tracker)
                cmds.menuItem(l=track, p=s.stabalize)
            cmds.button(s.go, e=True, en=True)

    def get_attr(s, gui):
        """ Grab attribute """
        cmds.textFieldButtonGrp(gui, e=True, tx=logic.get_attribute())

    def run(s, *_):
        """ Run everything! """
        tracker = s.data[cmds.optionMenu(s.tracker, q=True, v=True)]
        stab_key = cmds.optionMenu(s.stabalize, q=True, v=True)
        stabalize = [] if stab_key == NONE else s.data[stab_key]

        outX = cmds.textFieldButtonGrp(s.outX, q=True, tx=True)
        outY = cmds.textFieldButtonGrp(s.outY, q=True, tx=True)

        scale = cmds.intFieldGrp(s.scale, q=True, v=True)

        logic.apply_data(tracker, stabalize, outX, outY, scale[0], scale[1])
