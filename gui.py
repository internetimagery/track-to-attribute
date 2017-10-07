# Let thee control the stuff!
import maya.cmds as cmds

def temp():
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

NONE = "( None )"

class Window(object):
    def __init__(s):
        s.track_data = {}
        s.win = cmds.window("Tracker to Attribute")
        col = cmds.columnLayout(adj=True)
        s.nuke = cmds.textFieldButtonGrp(l="Nuke File:", bl="Browse", adj=2, bc=s.browse)
        s.tracker = cmds.optionMenuGrp(l="Tracker:", adj=2) + "|OptionMenu"
        s.stabalize = cmds.optionMenuGrp(l="Stabalize:", adj=2) + "|OptionMenu"
        s.outX = cmds.textFieldButtonGrp(l="Output X:", bl="<< CB", adj=2, bc=lambda:s.get_attr(s.outX))
        s.outY = cmds.textFieldButtonGrp(l="Output Y:", bl="<< CB", adj=2, bc=lambda:s.get_attr(s.outY))
        s.scale = cmds.intFieldGrp(l="Scale X / Y:", v1=1, v2=1, nf=2)
        s.go = cmds.button(l="Keyframe!", en=False, c=s.run)
        cmds.showWindow()

    def browse(s):
        """ Open file browser """
        # TODO: Put in proper file browse here!
        s.track_data = temp()

        # Clear out any existing tracks.
        remove = cmds.optionMenu(s.tracker, q=True, ill=True) or []
        remove += cmds.optionMenu(s.stabalize, q=True, ill=True) or []
        if remove:
            cmds.deleteUI(remove)
        # Add current tracks.
        cmds.menuItem(l=NONE, p=s.stabalize)
        for track in s.track_data:
            cmds.menuItem(l=track, p=s.tracker)
            cmds.menuItem(l=track, p=s.stabalize)
        cmds.button(s.go, e=True, en=True)

    def get_attr(s, gui):
        """ Grab attribute """
        print "Getting attribute"

    def run(s, *_):
        """ Run everything! """
        tracker = s.data[cmds.optionMenu(s.tracker, q=True, v=True)]
        stabalize = s.data[cmds.optionMenu(s.stabalize, q=True, v=True)]

        outX = cmds.textFieldButtonGrp(x.outX, q=True, tx=True)
        outY = cmds.textFieldButtonGrp(x.outY, q=True, tx=True)

        scale = cmds.intFieldGrp(s.scale, q=True, v=True)

        print tracker
        print stabalize
        print outX
        print outY
        print scale
