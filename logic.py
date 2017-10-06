# Make things work!
import maya.cmds as cmds
import subprocess
import os.path
import json

def get_tracker(file_path, nuke_path="nuke"):
    """ Get tracker data from nuke file """

    # Validate file and build command
    if not os.path.isfile(file_path):
        raise RuntimeError("File does not exist: {}".format(file_path))
    command = "{} -t -- '{}' '{}'".format(
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
            data = json.loads(line)
        except ValueError:
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
    for i, key in enumerate(keys):
        frame = i + startF
        cmds.setKeyframe(attr, t=frame, v=key)

def apply_data(tracker, stabalize, data, attrX, attrY, scaleX, scaleY):
    """ Take data. Apply it to attributes. """

    # Get data
    tracker_data = data[tracker]
    stabalize_data = data[stabalize] if stabalize else []

    # Calculate data
    dataX = []
    dataY = []
    for i, (x, y) in enumerate(zip(*tracker_data)):
        try:
            dataX.append((x - stabalize_data[0][i]) * scaleX)
            dataY.append((y - stabalize_data[1][i]) * scaleY)
        except IndexError:
            dataX.append(x * scaleX)
            dataY.append(x * scaleY)

    # Apply data
    start = cmds.currentTime(q=True)
    if attrX:
        set_keys(attrX, start, dataX)
    if attrY:
        set_keys(attrY, start, dataY)
