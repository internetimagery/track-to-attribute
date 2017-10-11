# Test parse thing.

import sys
import xml.etree.ElementTree as ET

def parse(file_):
    with open(file_, "r") as f:
        # for node in ET.fromstring(f.read()).find("./Project/NodesCollection") or []:
        for node in ET.fromstring(f.read()).findall("./Project/NodesCollection/item/TrackerContext/Item"):
            print node
            print node.find("Label").text

            # for tracker in node.find("TrackerContext") or []:
            #     try:
            #         name = tracker.find("Label").text
            #
            #         for n in tracker:
            #             try:
            #                 if n.find("Name").text == "centerPoint":
            #                     for p in n:
            #                         print(p)
            #                     # Perhaps keyframes reside here for tracker motion?
            #             except:
            #                 pass
            #     except AttributeError:
            #         pass



if __name__ == '__main__':
    from pprint import pprint
    parse(sys.argv[1])
