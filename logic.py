# Make things work!
from __future__ import print_function
import xml.etree.ElementTree as ET
import maya.cmds as cmds
import subprocess
import os.path
import base64
import re
try:
    import cPickle as pickle
except ImportError:
    import pickle

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

def get_attribute():
    """ Get selected attribute from channelbox """
    for obj in cmds.ls(sl=True) or []:
        for attr in cmds.channelBox("mainChannelBox", sma=True, q=True) or []:
            if cmds.attributeQuery(attr, n=obj, ex=True):
                return "{}.{}".format(obj, attr)
    return ""

def set_keys(attr, keys):
    """ Set keys on attribute """
    start = keys[min(keys.keys())]
    for frame in keys:
        cmds.setKeyframe(attr, t=frame, v=keys[frame] - start)

def apply_data(tracker, stabalize, attrX, attrY, scaleX, scaleY):
    """ Take data. Apply it to attributes. """
    if attrX == attrY:
        raise RuntimeError("Both attributes are the same.")

    attr = (attrX, attrY)
    scale = (scaleX, scaleY)
    data = ({},{})

    for i in range(len(tracker)):
        for frame in tracker[i]:
            try:
                data[i][frame] = (tracker[i][frame] - stabalize[i][frame]) * scale[i]
            except (KeyError, IndexError):
                data[i][frame] = tracker[i][frame] * scale[i]

    err = cmds.undoInfo(openChunk=True)
    try:
        for i in range(len(tracker)):
            if data[i] and attr[i]:
                set_keys(attr[i], data[i])
    except Exception as err:
        raise
    finally:
        # Do something undoable
        cmds.select(cmds.ls(sl=True), r=True)
        cmds.undoInfo(closeChunk=True)
        if err:
            cmds.undo()
