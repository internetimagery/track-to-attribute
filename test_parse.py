# Test parse thing.

import sys

def read_file(path):
    """ Read file character at a time """
    with open(path, "r") as f:
        while True:
            char = f.read(1)
            if not char:
                break
            yield char

def read_str(text):
    """ Read text character at a time """
    for char in text:
        yield char

def parse_escapes(connection, esc="\\"):
    """ Pull out escaped characters as chunks """
    escape = False
    token = ""
    for char in connection:
        escape = True if char == esc and escape else False
        token += char
        if not escape:
            yield token
            token = ""

def parse_brackets(connection, inB="{", outB="}"):
    """ Parse out bracketed chunks """
    depth = 1 # Assume we're already one deep
    token = ""
    for char in connection:
        if char == inB:
            depth += 1
        elif char == outB:
            depth -= 1
        if depth:
            token += char
        else:
            return token

def parse_line(connection, sep=" ", end="\n"):
    """ Parse out tokens """
    token = ""
    result = []
    for char in connection:
        if char == sep:
            token = token.strip()
            if token:
                result.append(token)
                token = ""
        elif char == end:
            token = token.strip()
            if token:
                result.append(token)
                token = ""
            yield result
            result = []
        else:
            token += char
            if char == "{":
                token = parse_brackets(connection).strip()
                if token:
                    result.append(token)
                    token = ""
    token = token.strip()
    if token:
        result.append(token)
    if result:
        yield result

def parse(path):
    """ Parse file path """
    for node in parse_line(read_file(path)):
        if node and node[0] == "Tracker4":
            for attr in parse_line(read_str(node[1])):
                if attr and attr[0] == "tracks":
                    for col, row in enumerate(parse_line(read_str(attr[1]))):
                        if col == 2: # Animation tracks
                            print row
                        #     for data in parse_line(read_str(row)):
                        #         print "HI"



if __name__ == '__main__':
    from pprint import pprint
    parse(sys.argv[1])
