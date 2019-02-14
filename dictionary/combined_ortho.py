# -*- coding: utf-8 -*-
import re

TABLE = None
TABLE_FILENAME = 'dict_sources/ortho.txt'


def substitute(s):
    table = load_table()
    return multiple_replace(table, s)


def multiple_replace(dict, text):
    # https://stackoverflow.com/a/15175239/4481448
    # Create a regular expression  from the dictionary keys
    regex = re.compile(u"(%s)" % u"|".join(map(re.escape, dict.keys())),
                       flags=re.UNICODE)

    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)


def load_table():
    global TABLE
    if TABLE is None:
        TABLE = {}
        with open(TABLE_FILENAME, 'rb') as infile:
            for line in infile:
                splits = line.decode('utf-8').strip().split(' ', 1)[1:]
                if len(splits) == 0:
                    continue
                if len(splits) != 1:
                    raise RuntimeError(line)
                line = splits[0]

                splits = line.split('\t')
                if len(splits) == 1:
                    continue
                if len(splits) != 2:
                    raise RuntimeError(line)
                TABLE[splits[0]] = splits[1]
    return TABLE


def transform_ortho():
    while True:
        try:
            line = raw_input().decode('utf-8')
        except (EOFError, IOError, KeyboardInterrupt):
            break

        print(substitute(line).encode('utf-8'))


if __name__ == '__main__':
    transform_ortho()
