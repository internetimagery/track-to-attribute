# Let thee control the stuff!
import maya.cmds as cmds
import logic
import os

def get_tracker():
    """ temporary return data for testing """
    return {
    "track1": [
        {0: 2, 1: 3, 4: 4, 5: 5},
        {0: 4, 1: 2, 4: 7, 5: 6}
        ],
    "other": [
        {0: 2, 1: 3, 4: 4, 5: 5},
        {0: 4, 1: 2, 4: 7, 5: 6}
        ]
    }

NONE = "---"

class Window(object):
    def __init__(s):
        s.data = {}
        s.win = cmds.window("Tracker to Attribute")
        col = cmds.columnLayout(adj=True)
        if os.name == "nt":
            s.nuke_exe = cmds.textFieldButtonGrp(l="Nuke executable:", bl="Browse", adj=2, bc=s.browse_nuke)
        s.nuke = cmds.textFieldButtonGrp(l="Nuke File:", bl="Browse", adj=2, bc=s.browse)
        s.tracker = cmds.optionMenuGrp(l="Tracker:", adj=2) + "|OptionMenu"
        cmds.menuItem(l=NONE, p=s.tracker)
        s.stabalize = cmds.optionMenuGrp(l="Stabalize:", adj=2) + "|OptionMenu"
        cmds.menuItem(l=NONE, p=s.stabalize)
        s.outX = cmds.textFieldButtonGrp(l="Output X:", bl="<< CB", adj=2, bc=lambda:s.get_attr(s.outX))
        s.outY = cmds.textFieldButtonGrp(l="Output Y:", bl="<< CB", adj=2, bc=lambda:s.get_attr(s.outY))
        s.scale = cmds.intFieldGrp(l="Scale X / Y:", v1=1, v2=1, nf=2)
        s.go = cmds.button(l="Keyframe!", en=False, c=s.run)
        cmds.showWindow()

    def browse_nuke(s):
        """ Pick nuke exe file """
        path = cmds.fileDialog2(fm=1, ff="Nuke executable (*.exe)")
        if path:
            cmds.textFieldButtonGrp(s.nuke_exe, e=True, tx=path[0])

    def browse(s):
        """ Open file browser """
        path = cmds.fileDialog2(fm=1, ff="Nuke files (*.nk)")
        if path:
            nuke_exe = cmds.textFieldButtonGrp(s.nuke_exe, q=True, tx=True) if os.name == "nt" else "nuke"
            s.data = logic.get_tracker(path[0], nuke_exe)

            # Clear out any existing tracks.
            remove = cmds.optionMenu(s.tracker, q=True, ill=True) or []
            remove += cmds.optionMenu(s.stabalize, q=True, ill=True) or []
            if remove:
                cmds.deleteUI(remove)
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
