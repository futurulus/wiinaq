# -*- coding: utf-8 -*-
"""
Run as: python combined_ortho.py < dict.mdf > dict_ortho.mdf
"""
import re

TABLE = None
TABLE_FILENAME = 'dict_sources/ortho.txt'


def substitute(s):
    table = load_table()
    return multiple_replace(table, s)


def multiple_replace(dict, text):
    # https://stackoverflow.com/a/15175239/4481448
    # Create a regular expression  from the dictionary keys
    options = "|".join(map(re.escape, dict.keys()))
    regex = re.compile(f'({options})', flags=re.UNICODE)

    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)


def load_table():
    global TABLE
    if TABLE is None:
        TABLE = {}
        with open(TABLE_FILENAME, 'rt') as infile:
            for line in infile:
                splits = line.strip().split(' ', 1)[1:]
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
            line = input()
        except (EOFError, IOError, KeyboardInterrupt):
            break

        print(substitute(line))


if __name__ == '__main__':
    transform_ortho()
