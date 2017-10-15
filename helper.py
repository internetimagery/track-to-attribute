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
        min_, max_ = 0
        for frame in keys:
            min_ = min(min_, keys[frame])
            max_ = max(max_, keys[frame])
        return min_, max_

    def scale(s, min_, max_):
        """ Scale keys to match a new min/max """
        diff1 = s.max - s.min
        diff2 = max_ - min_
        if diff1: # Don't continue if 0... no scaling!
            scale = (1 / diff1) * diff2
            s.keys = {f: (s.keys[f] - s.min) * scale + min_ for f in s.keys}
            s.min, s.max = s.get_range()


class Helper(object):
    def __init__(s):
        cmds.window(t="Key Match Helper")
        cmds.columnLayout(adj=True)
        s.text = cmds.text(l="things")
        s.value = cmds.intFieldGrp(l="Value:")
        cmds.rowLayout(nc=2)
        s.prev = cmds.button(l="Prev", en=False)
        s.next = cmds.button(l="Next")
        cmds.showWindow()
