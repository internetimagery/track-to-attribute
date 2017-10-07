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
    for frame in keys:
        cmds.setKeyframe(attr, t=frame, v=keys[frame])

def apply_data(tracker, stabalize, data, attrX, attrY, scaleX, scaleY):
    """ Take data. Apply it to attributes. """

    # Get data
    tracker_data = data[tracker]
    stabalize_data = data[stabalize] if stabalize else []

    # Calculate data
    dataX = {}
    dataY = {}
    def calc(data, stab, scale, output):
        for frame in data:
            try:
                output[frame] = (data[frame] - stab[frame]) * scale
            except KeyError:
                output[frame] = data[frame] * scale
    calc(tracker_data[0], stabalize_data[0], scaleX, dataX) # X
    calc(tracker_data[1], stabalize_data[1], scaleY, dataY) # Y

    # Apply data
    if dataX:
        set_keys(attrX, dataX)
    if dataY:
    if attrY:
