import re
from collections import namedtuple


def get_root(word):
    endings = ['luni', 'lutek', 'luteng', 'kunani', 'kunatek', 'kunateng',
               'luku', 'lukek', 'luki', 'kunaku', 'kunakek', 'kunaki']
    for ending in endings:
        if ending.startswith('l') and word.endswith('l' + ending):
            return word[:-len(ending) - 1] + 't'
        if ending.startswith('l') and (word.endswith('g' + ending) or
                                       word.endswith('t' + ending)):
            return word[:-len(ending)] + 't'
        if ending.startswith('k') and word.endswith('g' + ending):
            return word[:-len(ending) - 1]
        if word.endswith(ending):
            return word[:-len(ending)]

    neg_endings = ['inani', 'inatek', 'inateng', 'inaku', 'inakek', 'inaki']
    for ending in neg_endings:
        if word.endswith(ending):
            return word[:-len(ending)] + 'it'

    if re.search('(^|[^aeiou])[aeiou]teq$', word):
        return word[:-1] + 'r'
    elif word.endswith('teq'):
        return word[:-1]
    elif word.endswith('q'):
        return word[:-1] + 'r'

    return word


def apply_vowel_alternation(center, before):
    if center is None: return None

    if before is not None:
        before = get_root(before)
        if '(' in center[:2]:
            start_pos = center.index('(')
            end_pos = center.index(')')
            combine_cons = center[:start_pos]
            if before[-1:] in 'aeiou' or (combine_cons == '-' and
                                          before[-2:].startswith('e')):
                center = center[start_pos + 1:end_pos] + center[end_pos + 1:]
            else:
                center = center[:start_pos] + center[end_pos + 1:]

    return center


def apply_transformations(before, center, after):
    center = apply_vowel_alternation(center, before)
    after = apply_vowel_alternation(after, center)

    if after is not None:
        if after.startswith('-'):
            center = get_root(center)
            if center[-1] not in 'aeiou':
                center = center[:-1]
        elif after.startswith('~'):
            center = get_root(center)
            if after.startswith('~k'):
                if center.endswith('t'):
                    center = center[:-1] + 's'
                elif center[-1] not in 'aeiou':
                    center = center[:-1]
            elif after.startswith('~g'):
                if center[-1] not in 'aeiou':
                    center = center[:-1]
            elif after.startswith('~l'):
                center = get_root(center)
                if center.endswith('t'):
                    center = center[:-1]
        elif after.startswith('+'):
            center = get_root(center)
            if center.endswith('i') and after.startswith('+u'):
                center += 'y'

    if before is not None:
        before = get_root(before)
        if center.startswith('~k'):
            if before.endswith('r'):
                center = 'q' + center[2:]
            else:
                center = center[1:]
        elif center.startswith('~g'):
            if before.endswith('r'):
                center = 'r' + center[2:]
            else:
                center = center[1:]
        elif center.startswith('~l'):
            if len(before) >= 2 and before[-2] in 'aeiou' and before.endswith('t'):
                center = 'l' + center[1:]
            else:
                center = center[1:]
        elif center[0] in '+-~':
            center = center[1:]
        else:
            center = ' ' + center

    return center


def morpho_join(chunks):
    chunks = [None] + chunks + [None]
    transformed = []
    for i in range(1, len(chunks) - 1):
        transformed.append(apply_transformations(chunks[i - 1],
                                                 chunks[i],
                                                 chunks[i + 1]))
    return ''.join(transformed)


COLUMN_HEADERS = {
    'n': ['1', '2', '3+'],
    'vi': ['1', '2', '3+'],
}
ROW_HEADERS = {
    'n': ['-', 'gui', 'guangkunuk', 'guangkuta',
          'ellpet', "ellp'tek", "ellp'ci",
          'taugna', 'taugkuk', 'taugkut',
          'ellmenek', 'ellmegtegnek', 'ellmegtenek'],
    'vi': ['gui', 'ellpet', 'taugna', 'ellmenek'],
}
SECTION_HEADERS = {
    'n': ['normal', 'at', 'to', 'from', 'through', 'like', 'possessive'],
    'vi': ['present', 'past', 'conjunctive', 'dependent'],
}
ENDINGS = {
    'n': [
        [
            ['~k', '-k', '-t'],
            ['~ka', '-gka', '-nka'],
            ['~gpuk', '-puk', '-puk'],
            ['~gpet', '-pet', '-pet'],
            ['-n', '-gken', '-ten'],
            ['~gtek', '-tek', '-tek'],
            ['~gci', '-ci', '-ci'],
            ['-(~g)a', '-(~g)ak', '-(~ga)i'],
            ['-(~g)ak', '-(~ga)ik', '-(~ga)ik'],
            ['-(~g)at', '-(~ga)it', '-(~ga)it'],
        ]] + [
        [
            ['-men', '-nun', '-nun'] if ending == 'nun' else
            ['-gun', '-gun',  '-tgun'] if ending == 'kun' else
            ["-t'stun"] * 3 if ending == "t'stun" else
            ['-m' + ending[1:], '-' + ending, '-' + ending],
            ['-m' + ending] * 3,
            ['-mteg' + ending] * 3,
            ['-mte' + ending] * 3,
            ["~gp'" + ending] * 3,
            ["~gp'teg" + ending] * 3,
            ["~gp't's" + ending] * 3,
            ['-(~g)a' + ending, '-(~ga)i' + ending, '-(~ga)i' + ending],
            ['-(~g)ag' + ending, '-(~ga)ig' + ending, '-(~ga)ig' + ending],
            ['-(~g)at' + ending, '-(~ga)it' + ending, '-(~ga)it' + ending],
        ] for ending in ['ni', 'nun', 'nek', 'kun', "t'stun"]] + [
        [
            ["-m", "-k", "-t"],
            ["-ma", "-ma", "-ma"],
            ["-mnuk", "-mnuk", "-mnuk"],
            ["-mta", "-mta", "-mta"],
            ["-gpet", "-gpet", "-gpet"],
            ["-gp'tek", "-gp'tek", "-gp'tek"],
            ["-gp'ci", "-gp'ci", "-gp'ci"],
            ["-n", "-(~ga)ini", "-(~ga)ini"],
            ["-gta", "-(~ga)igta", "-(~ga)igta"],
            ["-ta", "-(~ga)ita", "-(~ga)ita"],
        ]
    ],
    'vi': [
        [
            ['+(+g)ua', '+ukuk', '+ukut'],
            ['+uten', '+utek', '+uci'],
            ['+uq', '+uk', '+ut'],
        ],
        [
            ['-llrianga', '-llriakuk', '-llriakut'],
            ['-llriaten', '-llriatek', '-llriaci'],
            ['-llria', '-llriik', '-llriit'],
        ],
        [
            ['~lua(nga)', '~lunuk', '~luta'],
            ['~luten', '~lutek', '~luci'],
            ['~luni', '~lutek', '~luteng'],
        ],
        [
            ['~kuma', '~kumnuk', '~kumta'],
            ['~kut', '~kumtek', '~kumci'],
            ['~kan', '~kagta', '~kata'],
            ['~kuni', '~kunek', '~kuneng'],
        ],
    ],
}

TableRow = namedtuple('TableRow', ['header', 'cells'])
TableSection = namedtuple('TableSection', ['title', 'column_headers', 'rows'])

def inflection_data(chunk):
    if chunk.pos in ENDINGS:
        return {'inflections': inflect(chunk.entry,
                                       ENDINGS[chunk.pos],
                                       SECTION_HEADERS[chunk.pos],
                                       COLUMN_HEADERS[chunk.pos],
                                       ROW_HEADERS[chunk.pos])}
    else:
        return {'inflections': None}


def build_section(title, column_headers, rows):
    num_columns = max(len(r.cells) for r in rows)
    return TableSection(title, column_headers[:num_columns], rows)


def inflect(entry, cells, section_headers, column_headers, row_headers):
    return [build_section(s, column_headers,
            [TableRow(rh, [morpho_join([entry, c]) for c in row])
             for rh, row in zip(row_headers, cells[i])])
            for i, s in enumerate(section_headers)]
