# Test parse thing.

import sys
import xml.etree.ElementTree as ET

def parse(file_):
    with open(file_, "r") as f:
        root = ET.fromstring(f.read())
        print(root.findall("TrackerContext"))

if __name__ == '__main__':
    from pprint import pprint
    parse(sys.argv[1])
