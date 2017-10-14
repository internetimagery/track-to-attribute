# Make things work!
from __future__ import print_function, division
import xml.etree.ElementTree as ET
import maya.cmds as cmds
import subprocess
import os.path
import base64
import math
import re
try:
    import cPickle as pickle
except ImportError:
    import pickle

def parse_nuke_frames(curve):
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
            X = parse_nuke_frames(tracker.group(2))
            Y = parse_nuke_frames(tracker.group(3))
            result[tracker.group(1)] = {f: (X[f], Y[f]) for f in X}
    return result

def parse_natron_frames(curve):
    """ Pull out frame data """
    result = {}
    for key in curve.findall("item"):
        result[key.find("Time").text] = float(key.find("Value").text)
    return result

def parse_natron(file_):
    """ Parse out data from Natron """
    print("Reading Natron file.")
    result = {}
    for node in ET.fromstring(file_).findall("./Project/NodesCollection/item/TrackerContext/Item"):
        X, Y = [parse_natron_frames(a) for a in node.findall("Item/[Name='centerPoint']/item/Curve/KeyFrameSet")]
        result[node.find("Label").text] = {f: (X[f], Y[f]) for f in X}
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

def get_attribute():
    """ Get selected attribute from channelbox """
    for obj in cmds.ls(sl=True) or []:
        for attr in cmds.channelBox("mainChannelBox", sma=True, q=True) or []:
            if cmds.attributeQuery(attr, n=obj, ex=True):
                return "{}.{}".format(obj, attr)
    return ""

def get_angle(aX, aY, bX, bY):
    """ Get angle of difference vector from (0,1) base """
    diff = (bX-aX, bY-aY)
    mag = math.sqrt(sum(a*a for a in diff))
    norm = [a/mag if a else 0 for a in diff]
    return math.degrees(math.atan2(*norm) - math.atan2(0, 1))

def set_keys(attr, keys):
    """ Set keys on attribute """
    start = keys[min(keys.keys())]
    for frame in keys:
        cmds.setKeyframe(attr, t=frame, v=keys[frame] - start)

def apply_data(tracker, stabalize, attrX, attrY, attrA, scaleX, scaleY):
    """ Take data. Apply it to attributes. """
    if attrX and attrY and attrX == attrY:
        raise RuntimeError("Both attributes are the same.")

    attr = (attrX, attrY)
    scale = (scaleX, scaleY)
    data = {}
    angle = {}

    # Calculate stability
    for frame in tracker:
        try:
            data[frame] = [a - b for a, b in zip(tracker[frame], stabalize[frame])]
        except KeyError:
            data[frame] = tracker[frame]

    # Scale!
    for frame in data:
        data[frame] = [data[a] * b for a, b in zip(data, scale)]

    # Calculate angle
    for frame in tracker:
        try:
            angle[frame] = get_angle(
                tracker[frame][0],
                tracker[frame][1],
                stabalize[frame][0],
                stabalize[frame][1])
        except KeyError:
            pass

    err = cmds.undoInfo(openChunk=True)
    try:
        for i in range(len(tracker)):
            if data[i] and attr[i]:
                set_keys(attr[i], data[i])
        if attrA and angle:
            set_keys(attrA, angle)
    except Exception as err:
        raise
    finally:
        # Do something undoable
        cmds.select(cmds.ls(sl=True), r=True)
        cmds.undoInfo(closeChunk=True)
        if err:
            cmds.undo()
