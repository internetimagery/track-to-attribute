# Make things work!
from __future__ import print_function, division
import xml.etree.ElementTree as ET
import subprocess
import os.path
import base64
import math
import re
try:
    import cPickle as pickle
except ImportError:
    import pickle

X, Y = 0, 1

def real_path(path):
    """ Get closest real path up the tree """
    while True:
        new_path = os.path.dirname(path)
        if new_path == path:
            return ""
        elif os.path.isdir(new_path):
            return new_path

class Keyset(object):
    def __init__(s, keys):
        """ Accepts {frame: value} """
        s.data = keys
        s.set_range()

    def set_range(s):
        """ Return min and max keyframe values """
        for i, frame in enumerate(s.data):
            value = s.data[frame]
            if not i:
                min_ = (frame, value)
                max_ = (frame, value)
            tmp_min = min(min_[1], value)
            tmp_max = max(max_[1], value)
            if value == tmp_min:
                min_ = (frame, value)
            if value == tmp_max:
                max_ = (frame, value)
        s.min = min_
        s.max = max_

    def scale(s, min_, max_):
        """ Scale keys to match a new min/max """
        diff1 = s.max[1] - s.min[1]
        diff2 = max_ - min_
        if diff1: # Don't continue if 0... no scaling!
            scale = (1 / diff1) * diff2
            s.data = {f: (s.data[f] - s.min[1]) * scale + min_ for f in s.data}
            s.set_range()

def parse_frames(curve):
    """ Parse out keyframes from nuke curve data """
    result = {}
    frame = 0
    for num in curve.split(" "):
        if num[0] == "x":
            frame = int(num[1:])
        else:
            result[frame] = float(num)
            frame += 1
    return result

def parse_nuke(file_):
    """ Parse out data from nuke """
    print("Reading Nuke file.")
    result = {}
    nodes = re.compile(r"Tracker4\s{.+?ypos[-\d\n\s]+}", re.DOTALL)
    trackers = re.compile(r"\"((?:\\.|[^\"\\])*)\"\s+{curve\s+([-\d\.\sex]+)}\s+{curve\s+([-\d\.\sex]+)}") # :: "tracker" {curve x12 34.56 67.54-e32 43.4554}
    for node in nodes.finditer(file_):
        for tracker in trackers.finditer(node.group(0)):
            result[tracker.group(1)] = (
                parse_frames(tracker.group(2)),
                parse_frames(tracker.group(3))
                )
    return result

def parse_natron(file_):
    """ Parse out data from Natron """
    print("Reading Natron file.")
    result = {}
    for node in ET.fromstring(file_).findall("./Project/NodesCollection/item/TrackerContext/Item"):
        curves = []
        for curve in node.findall("Item/[Name='centerPoint']/item/Curve/KeyFrameSet"):
            keys = {}
            for key in curve.findall("item"):
                keys[float(key.find("Time").text)] = float(key.find("Value").text)
            curves.append(keys)
        result[node.find("Label").text] = curves
    return result

def get_tracks(file_path):
    """ Get Tracker data. """
    if not os.path.isfile(file_path):
        raise RuntimeError("File does not exist: {}".format(file_path))
    with open(file_path, "r") as f:
        if file_path[-3:] == ".nk":
            return parse_nuke(f.read())
        elif file_path[-4:] == ".ntp":
            return parse_natron(f.read())
        else:
            raise RuntimeError("File type not (yet) supported.")

def get_angle(aX, aY, bX, bY):
    """ Get angle of difference vector from (0,1) base """
    diff = (bX-aX, bY-aY)
    mag = math.sqrt(sum(a*a for a in diff))
    norm = [a/mag if a else 0 for a in diff]
    return math.degrees(math.atan2(*norm) - math.atan2(0, 1))

def process_keys(axis, start, end, tracker1, tracker2=[]):
    """ Process keyframes. Stabalize / Angle(ify) """
    result = {}
    if axis == "angle":
        for frame in tracker1[X]:
            if frame >= start and frame <= end:
                try:
                    result[frame] = get_angle(
                        tracker1[X][frame],
                        tracker1[Y][frame],
                        tracker2[X][frame],
                        tracker2[Y][frame])
                    except (KeyError, IndexError):
                        pass
    else:
        ax = 0 if axis == "X" else 1
        for frame in tracker1[ax]:
            if frame >= start and frame <= end:
                try:
                    result[frame] = tracker1[ax][frame] - tracker2[ax][frame]
                except (KeyError, IndexError):
                    result[frame] = tracker1[ax][frame]
    return Keyset(result) if result else None

def apply_data(tracker, stabalize, attrX, attrY, attrA, scaleX, scaleY, start, stop, callback):
    """ Take data. Apply it to attributes. """
    if attrX and attrY and attrX == attrY:
        raise RuntimeError("Both attributes are the same.")

    attr = (attrX, attrY)
    scale = (scaleX, scaleY)
    data = ({},{})
    angle = {}

    # Calculate stability and scale
    for i in range(len(tracker)):
        for frame in tracker[i]:
            if frame >= start and frame <= stop:
                try:
                    data[i][frame] = (tracker[i][frame] - stabalize[i][frame]) * scale[i]
                except (KeyError, IndexError):
                    data[i][frame] = tracker[i][frame] * scale[i]

    # Calculate angle
    for frame in tracker[0]:
        if frame >= start and frame <= stop:
            try:
                angle[frame] = get_angle(
                    tracker[0][frame],
                    tracker[1][frame],
                    stabalize[0][frame],
                    stabalize[1][frame])
            except (KeyError, IndexError):
                pass

    result = {}
    if attrX and data[0]:
        result[attrX] = Keyset(data[0])
    if attrY and data[1]:
        result[attrY] = Keyset(data[1])
    if attrA and angle:
        result[attrA] = Keyset(angle)
    if result:
        callback(result)
