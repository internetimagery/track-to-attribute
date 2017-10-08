# Make things work!
import maya.cmds as cmds
import subprocess
import os.path
import base64
try:
    import cPickle as pickle
except ImportError:
    import pickle

def get_tracker(file_path, nuke_path="nuke"):
    """ Get tracker data from nuke file. """

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

def get_attribute():
    """ Get selected attribute from channelbox """
    for obj, attr in zip(cmds.ls(sl=True) or [], cmds.channelBox("mainChannelBox", sma=True, q=True) or []):
        if cmds.attributeQuery(attr, n=obj, ex=True):
            return "{}.{}".format(obj, attr)
    return ""

def set_keys(attr, startF, keys):
    """ Set keys on attribute """
    start = keys[min(sorted(keys.keys()))]
    for frame in keys:
        cmds.setKeyframe(attr, t=frame, v=keys[frame] - start)

def apply_data(tracker, stabalize, attrX, attrY, scaleX, scaleY):
    """ Take data. Apply it to attributes. """
    if attrX == attrY:
        raise RuntimeError("Both attributes are the same.")

        attr = (attrX, attrY)
        scale = (scaleX, scaleY)

        # Calculate data
        dataX = {}
        dataY = {}
        def calc(data, stab, scale, output):
            for frame in data:
                try:
                    output[frame] = (data[frame] - stab[frame]) * scale
                except KeyError:
                    output[frame] = data[frame] * scale
        calc(tracker[0], stabalize[0], scaleX, dataX) # X
        calc(tracker[1], stabalize[1], scaleY, dataY) # Y

    err = cmds.undoInfo(openChunk=True)
    try:
        # Apply data
        if dataX:
            set_keys(attrX, dataX)
        if dataY:
            set_keys(attrY, dataY)
    except Exception as err:
        raise
    finally:
        cmds.undoInfo(closeChunk=True)
        if err:
            cmds.undo()
