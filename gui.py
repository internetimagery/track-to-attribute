# Let thee control the stuff!
from __future__ import print_function, division
import maya.cmds as cmds
import logic
import os

NONE = "---"


def get_attribute():
    """ Get selected attribute from channelbox """
    for obj in cmds.ls(sl=True) or []:
        for attr in cmds.channelBox("mainChannelBox", sma=True, q=True) or []:
            if cmds.attributeQuery(attr, n=obj, ex=True):
                return "{}.{}".format(obj, attr)
    return ""

class Helper(object):
    def __init__(s, data):
        """ Helper GUI to collect range information. {attr: {frame: value}} """
        s.data = data
        s.state = []
        for attr in s.data:
            s.state.append({ "attr": attr, "time": s.data[attr].min[0]})
            s.state.append({ "attr": attr, "time": s.data[attr].max[0]})
        s.state_pos = 0
        print(s.state)

        s.win = cmds.window(t="Key Match")
        cmds.columnLayout(adj=True)
        cmds.text(l="Please position attribute:")
        s.text = cmds.text(l="ATTR", hl=True)
        cmds.separator()
        s.capt = cmds.button(l="Capture Attribute", c=s.capture)
        cmds.showWindow()
        s.refresh()

    def refresh(s):
        """ Set gui to capture frame """
        attr = s.state[s.state_pos]["attr"]
        time = s.state[s.state_pos]["time"]
        cmds.text(s.text, e=True, l="<h1>{} : {}</h1>".format(attr.split(".")[0], cmds.attributeName(attr, n=True)))
        cmds.currentTime(time)

    def capture(s, *_):
        """ Set capture attribute at time """
        attr = s.state[s.state_pos]["attr"]
        time = s.state[s.state_pos]["time"]
        s.state[s.state_pos]["val"] = cmds.getAttr(attr, t=time)
        s.state_pos += 1
        if s.state_pos < len(s.state):
            s.refresh()
        else:
            # Scale keyframes!
            for i in range(0, len(s.state), 2):
                attr = s.state[i]["attr"]
                min_ = s.state[i]["val"]
                max_ = s.state[i+1]["val"]
                s.data[attr].scale(min_, max_)

            err = cmds.undoInfo(openChunk=True)
            try:
                for attr in s.data:
                    for frame in s.data[attr].data:
                        value = s.data[attr].data[frame]
                        cmds.setKeyframe(attr, t=frame, v=value)
            except Exception as err:
                raise
            finally:
                cmds.undoInfo(closeChunk=True)
                if err:
                    cmds.undo()
            cmds.deleteUI(s.win, window=True)

class Window(object):
    def __init__(s):
        s.data = {}
        s.win = cmds.window("Tracker to Attribute")
        col = cmds.columnLayout(adj=True)
        s.nuke = cmds.textFieldButtonGrp(l="Tracker File:", bl="Browse", adj=2, bc=s.browse, cc=s.load_tracker)
        s.tracker = cmds.optionMenuGrp(l="Tracker:", adj=2) + "|OptionMenu"
        s.stabalize = cmds.optionMenuGrp(l="Stabalize / Angle:", adj=2) + "|OptionMenu"
        s.outX = cmds.textFieldButtonGrp(l="Output X:", bl="<< CB", adj=2, bc=lambda:s.get_attr(s.outX))
        s.outY = cmds.textFieldButtonGrp(l="Output Y:", bl="<< CB", adj=2, bc=lambda:s.get_attr(s.outY))
        s.outA = cmds.textFieldButtonGrp(l="Angle:", bl="<< CB", adj=2, bc=lambda:s.get_attr(s.outA))
        s.scale = cmds.intFieldGrp(l="Scale X / Y:", v1=1, v2=1, nf=2)
        s.view = cmds.checkBoxGrp(l="Restrict to range:", v1=True)
        s.go = cmds.button(l="Keyframe!", en=False, c=s.run)
        cmds.showWindow()

    def browse(s):
        """ Open file browser """
        path = cmds.fileDialog2(
            fm=1,
            ff="Tracker file (*.nk *.ntp)",
            dir=logic.real_path(cmds.textFieldButtonGrp(s.nuke, q=True, tx=True)))
        if path:
            s.load_tracker(path[0])

    def load_tracker(s, path):
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
        cmds.textFieldButtonGrp(gui, e=True, tx=get_attribute())

    def run(s, *_):
        """ Run everything! """
        tracker = s.data[cmds.optionMenu(s.tracker, q=True, v=True)]
        stab_key = cmds.optionMenu(s.stabalize, q=True, v=True)
        stabalize = [] if stab_key == NONE else s.data[stab_key]

        outX = cmds.textFieldButtonGrp(s.outX, q=True, tx=True)
        outY = cmds.textFieldButtonGrp(s.outY, q=True, tx=True)
        outA = cmds.textFieldButtonGrp(s.outA, q=True, tx=True)


        scale = cmds.intFieldGrp(s.scale, q=True, v=True)
        view = cmds.checkBoxGrp(s.view, q=True, v1=True)

        Fstart = cmds.playbackOptions(q=True, min=True) if view else -99999
        Fstop = cmds.playbackOptions(q=True, max=True) if view else 99999


        logic.apply_data(
            tracker,
            stabalize,
            outX,
            outY,
            outA,
            scale[0],
            scale[1],
            Fstart,
            Fstop,
            Helper)
