# Redesign.
#
# Load file prompt directly when opening the gui.
# No need to check for file existance or updates etc.


# add as many attributes as wanted in order to work on them at once.
# button "new" create a new entry.
# entry: [x/y/angle] [track] [stabalize/angle] [remove]

import maya.cmds as cmds
import maya.mel as mel
import logic

NONE = "---"


def get_attribute():
    """ Get selected attribute from channelbox """
    return set("{}.{}".format(o, at) for o in cmds.ls(sl=True) for at in cmds.channelBox("mainChannelBox", sma=True, q=True) or [] if cmds.attributeQuery(at, n=o, ex=True))

def browse():
    """ Open file browser """
    path = cmds.fileDialog2(
        fm=1,
        ff="Tracker file (*.nk *.ntp)",
        dir=logic.real_path(cmds.textFieldButtonGrp(s.nuke, q=True, tx=True)))
    if path:
        s.load_tracker(path[0])

class Helper(object):
    def __init__(s, data):
        """ Helper GUI to collect range information. {attr: Keyset()} """
        s.data = data
        s.state = []
        for attr in s.data:
            s.state.append({ "attr": attr, "time": s.data[attr].min[0]})
            s.state.append({ "attr": attr, "time": s.data[attr].max[0]})
        s.state_pos = 0

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

class Attribute(object):
    """ Attribute gui entry """
    def __init__(s, parent, attr, trackers, callback):
        s._active = True
        s._callback = callback
        s._attr = cmds.textField(w=400, tx=attr, p=parent)
        s._axis = cmds.optionMenu(p=parent)
        for t in logic.AXIS:
            cmds.menuItem(l=t, p=s._axis)
        s._track1 = cmds.optionMenu(p=parent)
        for t in trackers:
            cmds.menuItem(l=t, p=s._track1)
        s._track2 = cmds.optionMenu(p=parent)
        for t in trackers:
            cmds.menuItem(l=t, p=s._track2)
        s._key = cmds.button(l="Key", c=s.key, bgc=(0.2, 0.5, 0.4), p=parent)
        s._del = cmds.button(l="Remove", c=s.delete, bgc=(0.4, 0.3, 0.3), p=parent)
    def key(s, *_):
        """ Key attr data """
        if s._active:
            s._callback([[s.attr, s.axis, s.track1, s.track2]])
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
            cmds.showWindow()

    def clear_all(s, *_):
        """ Remove all attrs """
        for at in s.attributes:
            at.delete()
        s.attributes = []

    def key_all(s, *_):
        """ Key all """
        s.set_keys((at.attr, at.axis, at.track1, at.track2) for at in s.attributes)

    def add_attr(s, *_):
        """ Add new attribute from channelbox """
        attrs = get_attribute()
        for at in attrs:
            s.attributes.append(Attribute(s.root, at, s.trackers, s.set_keys))

    def set_keys(s, info):
        """ Finally start the key setting process """
        print info
        data = [at for (at, ax, t1, t2) in info]
        print data
        return

        # Get frame range we're working in
        slider = mel.eval("$tmp = $gPlayBackSlider")
        if cmds.timeControl(slider, q=True, rv=True): # Check if we have highlighted the timeline
            Fstart, Fstop = cmds.timeControl(slider, q=True, ra=True)
        else:
            Fstart = cmds.playbackOptions(q=True, min=True)
            Fstop = cmds.playbackOptions(q=True, max=True)

        # Process data
        data = {
            at: logic.process_keys(ax, Fstart, Fstop, s.data[t1] if t1 != NONE else [], s.data[t2] if t2 != NONE else [])
            for (at, ax, t1, t2) in info}

        # Set keyframes
        if data:
            Helper(data)
