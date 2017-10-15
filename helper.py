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
        s.data = [{"attr": at, "keys": Keyset(data[at])} for at in data]
        win = cmds.window(t="Key Match Helper")
        cmds.columnLayout(adj=True)
        cmds.text(l="Please set attribute:")
        s.text = cmds.text(l="ATTR")
        s.capt = cmds.button(l="Capture Attribute")
        cmds.showWindow()

    def doit(s, attr, time, callback):
        """ Set capture attribute at time """
        cmds.text(s.text, e=True, l=attr)
        def cb(*_):
            callback(cmds.getattr(attr, t=time))
        cmds.button(s.capt. e=True, c=cb)
        cmds.currentTime(time)
