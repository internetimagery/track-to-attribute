# Parse out tracker data.
from __future__ import print_function
import json
import re

def run(file_path):
    """ Pull out tracker data and pass it to calling process """

    import nuke
    nuke.scriptClear()
    nuke.scriptOpen(file_path)

    trackers = {}

    for node in (n["tracks"].toScript() for n in nuke.allNodes() if n.Class() == "Tracker4"):
        for track in re.finditer(r"\"([^\"])\"\s*{\s*curve\s*x\d+\s*([\d\s\.\-xe])}\s*{\s*curve\s*x\d+\s*([\d\s\.\-xe])}", node):
            name = track.group(1)
            X = (a for a in track.group(2).split(" ") if a[0] != "x")
            y = (a for a in track.group(3).split(" ") if a[0] != "x")
            trackers[name] = (x, y)

    print(json.dumps(trackers))
    return True

if __name__ == '__main__':
    import sys
    sys.exit(run(sys.argv[1]) is False)
