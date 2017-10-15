# Help match animation. GUI!
from __future__ import print_function, division

# goals!

# get min and max keyframe value
# set attribute to value and provide tools to adjust
# collect information then scale keys based on the info
# set keyframes


class Keyset(object):
    def __init__(s, keys):
        """ Accepts {frame: value} """
        s.data = keys
        s.min, s.max = s.get_range(keys)

    def get_range(keys):
        """ Return min and max keyframe values """
        min_, max_ = (0, 0)
        for frame in keys:
            value = keys[frame]
            tmp_min = min(min_[1], value)
            tmp_max = max(max_[1], value)
            if value == tmp_min:
                min_ = (frame, value)
            if value == tmp_max:
                max_ = (frame, max_)
        return min_, max_

    def scale(s, min_, max_):
        """ Scale keys to match a new min/max """
        diff1 = s.max[1] - s.min[1]
        diff2 = max_ - min_
        if diff1: # Don't continue if 0... no scaling!
            scale = (1 / diff1) * diff2
            s.keys = {f: (s.keys[f] - s.min[1]) * scale + min_ for f in s.keys}
            s.min, s.max = s.get_range()


class Helper(object):
    def __init__(s, data):
        """ Helper GUI to collect range information. {attr: {frame: value}} """
        s.data = {at: Keyset(data[at]) for at in data}
        s.state = []
        for attr in s.data:
            s.state.append({ "attr": attr, "time": s.data[attr].min[0]})
            s.state.append({ "attr": attr, "time": s.data[attr].max[0]})
        s.state_pos = 0

        win = cmds.window(t="Key Match")
        cmds.columnLayout(adj=True)
        cmds.text(l="Please position attribute:")
        s.text = cmds.text(l="ATTR")
        s.capt = cmds.button(l="Capture Attribute", s.capture)
        cmds.showWindow()

    def refresh(s):
        """ Set gui to capture frame """
        attr = s.state[s.state_pos]["attr"]
        time = s.state[s.state_pos]["time"]
        cmds.text(s.text, e=True, l=attr)
        cmds.currentTime(time)

    def capture(s, *_):
        """ Set capture attribute at time """
        attr = s.state[s.state_pos]["attr"]
        time = s.state[s.state_pos]["time"]
        s.state[s.state_pos]["val"] = cmds.getattr(attr, t=time)
        s.state_pos += 1
        if s.state_pos < len(s.state):
            s.refresh()
        else:
            print(s.state)
