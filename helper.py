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

class State(object):
    def __init__(s, attr, keys):
        """ Manage state collecting data for scaling """
        s.state = 0 # 0 = min, 1 = max
        s.attr = attr
        s.keys = Keyset(keys)
        s.curr_min = cmds.getattr(attr, t=s.keys.min[0])
        s.curr_max = cmds.getattr(attr, t=s.keys.max[0])


class Helper(object):
    def __init__(s, attr, keys):
        """ Helper GUI to collect range information. """
        s.autokey = cmds.autoKeyframe(state=True, q=True)
        cmds.autoKeyframe(state=False)
        win = cmds.window(t="Key Match Helper")
        cmds.columnLayout(adj=True)
        s.text = cmds.text(l="things")
        s.value = cmds.intFieldGrp(l="Value:")
        cmds.rowLayout(nc=2)
        s.prev = cmds.button(l="Prev", en=False)
        s.next = cmds.button(l="Next")
        cmds.showWindow()
        cmds.scriptJob(uid=(win, s.cleanup))

    def cleanup(s):
        """ Undo any changes made etc """
        cmds.autoKeyframe(state=s.autokey)

    def doit(s):
        """ Set frame to min and max fields """

        pass
