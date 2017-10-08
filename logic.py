# Make things work!
from __future__ import print_function
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
    """ Parse out keyframes from data """
    result = {}
    frame = 0
    for num in curve.split(" "):
        if num[0] == "x":
            frame = int(num[1:])
        else:
            result[frame] = float(num)
            frame += 1
    return result

def get_tracks_direct(filepath):
    """ Read out some info from Nuke file """
    with open(filepath, "r") as f:
        tracks = re.compile(r"tracks.+?\s(\d+)\s+(\d+)\s+}", re.DOTALL) # :: tracks { { 1 2 3 }
        parse = re.compile(r"\"([^\"]+)\"\s+{curve\s+([-\d\.\sex]+)}\s+{curve\s+([-\d\.\sex]+)}") # :: "tracker" {curve x12 34.56 67.54-e32 43.4554}
        wait = 0 # Throwing out the header
        curve = 0 # Reading our curves
        reading_tracker = False # In a node we can handle?
        while True:
            # Run through each line
            line = f.readline()
            if not line:
                break
            if line.startswith("Tracker4"):
                reading_tracker = True
            if wait: # We have a tracker nodes "tracks" knob
                wait -= 1
            elif curve: # We're looking at a curves data
                curve -= 1
                match = parse.search(line)
                if match:
                    yield (match.group(1), parse_frames(match.group(2)), parse_frames(match.group(3))) # Name, X, Y
            elif reading_tracker: # Looking for a tracker
                match = tracks.search(line)
                if match:
                    wait = int(match.group(1)) + 2 # Plus 2 for closing and opening brackets
                    curve = int(match.group(2))
                    reading_tracker = False

def get_tracks_indirect(file_path, nuke_path="nuke"):
    """ Get tracker data from nuke file, by loading nuke. """

    # Validate file and build command
    if not os.path.isfile(file_path):
        raise RuntimeError("File does not exist: {}".format(file_path))
    command = "\"{}\" -t -- \"{}\" \"{}\"".format(
        nuke_path,
        os.path.join(os.path.dirname(__file__), "track_parse.py"),
        file_path)

    # Run nuke and collect data.
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    data = {}
    while True:
        line = process.stdout.readline()
        if not line:
            break
        try:
            data = pickle.loads(base64.b64decode(line))
        except TypeError, pickle.UnpicklingError:
            pass
    err = process.stderr.read()
    if err:
        raise RuntimeError(err)
    return data

def get_tracks(file_path, nuke="nuke"):
    """ Get Tracker data first by parsing nuke file and otherwise by loading nuke """
    # First parse the file directly.
    try:
        result = {}
        for name, x, y in get_tracks_direct(file_path):
            result[name] = (x, y)
        return result
    except Exception as err:
        print("Failed to parse Nuke. Falling back to loading nuke.. {}".format(err))
        return get_tracks_indirect(file_path, nuke)

def get_attribute():
    """ Get selected attribute from channelbox """
    for obj, attr in zip(cmds.ls(sl=True) or [], cmds.channelBox("mainChannelBox", sma=True, q=True) or []):
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
        cmds.select(cmds.ls(sl=True))
        cmds.undoInfo(closeChunk=True)
        if err:
            cmds.undo()
