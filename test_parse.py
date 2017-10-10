# Test parse thing.

import sys

def read_char(path):
    """ Read file character at a time """
    with open(path, "r") as f:
        while True:
            char = f.read(1)
            if not char:
                break
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
        token += char
        if char == inB:
            depth += 1
        elif char == outB:
            depth -= 1
        if not depth:
            return token

def parse_line(connection, sep=" ", end="\n"):
    """ Parse out tokens """
    token = ""
    result = []
    for char in connection:
        if char == sep:
            result.append(token)
            token = ""
        elif char == end:
            result.append(token)
            yield result
            result = []
            token = ""
        else:
            token += char
            if char == "{":
                result.append(parse_brackets(connection))
                token = ""
    if result:
        yield result

def parse(path):
    """ Parse file path """
    connection = read_char(path)
    for line in parse_line(connection):
        print line



if __name__ == '__main__':
    from pprint import pprint
    parse(sys.argv[1])
