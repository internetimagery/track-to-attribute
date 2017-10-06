# Parse out tracker data.
from __future__ import print_function
import json
import re

def run(file_path):
    """ Pull out tracker data and pass it to calling process """

    # Bring in file
    import nuke
    nuke.scriptClear()
    nuke.scriptOpen(file_path)

    # Parse tracker data
    trackers = {}
    for node in (n["tracks"].toScript() for n in nuke.allNodes() if n.Class() == "Tracker4"):
        for track in re.finditer(r"\"([^\"])\"\s*{\s*curve\s*([\d\s\.\-xe])}\s*{\s*curve\s*([\d\s\.\-xe])}", node):
            name = track.group(1)
            X = (float(a) for a in track.group(2).split(" ") if a[0] != "x")
            y = (float(a) for a in track.group(3).split(" ") if a[0] != "x")
            trackers[name] = (x, y)

    # Send tracker data back to calling process
    print(json.dumps(trackers))
    return True

if __name__ == '__main__':
    import sys
    sys.exit(run(sys.argv[1]) is False)
