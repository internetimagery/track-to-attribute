# Parse out tracker data.
from __future__ import print_function
import re
import base64
try:
    import cPickle as pickle
except ImportError:
    import pickle

def parse_curve(curve):
    """ Parse curve data to dict """
    frame = 0
    result = {}
    for c in curve.split(" "):
        if c[0] == "x": # Frame number
            frame = int(c[1:])
        else:
            result[frame] = float(c)
            frame += 1
    return result

def run(file_path):
    """ Pull out tracker data and pass it to calling process """

    # Bring in file
    import nuke
    nuke.scriptClear()
    nuke.scriptOpen(file_path)

    # Parse tracker data
    trackers = {}
    for node in (n["tracks"].toScript() for n in nuke.allNodes() if n.Class() == "Tracker4"):
        for track in re.finditer(r"\"([^\"]+)\"\s+{\s*curve\s+([\d\s\.\-xe]+)}\s+{\s*curve\s+([\d\s\.\-xe]+)}", node):
            name = track.group(1)
            x = parse_curve(track.group(2))
            y = parse_curve(track.group(3))
            trackers[name] = (x, y)

    # Send tracker data back to calling process
    print(base64.b64encode(pickle.dumps(trackers)))
    return True

if __name__ == '__main__':
    import sys
    sys.exit(run(sys.argv[1]) is False)
