# Test parse thing.

import sys
import xml.etree.ElementTree as ET

def parse(file_):
    with open(file_, "r") as f:
        # for node in ET.fromstring(f.read()).find("./Project/NodesCollection") or []:
        result = {}
        for node in ET.fromstring(f.read()).findall("./Project/NodesCollection/item/TrackerContext/Item"):
            name = node.find("Label").text
            curves = []
            for curve in node.findall("Item/[Name='centerPoint']/item/Curve/KeyFrameSet"):
                keys = {}
                for key in curve.findall("item"):
                    keys[float(key.find("Time").text)] = float(key.find("Value").text)
                curves.append(keys)
            result[name] = curves
        return result



if __name__ == '__main__':
    from pprint import pprint
    print parse(sys.argv[1])
