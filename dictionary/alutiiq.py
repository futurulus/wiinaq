import re
from collections import namedtuple


def get_root(word):
    endings = ['luni', 'lutek', 'luteng', 'kunani', 'kunatek', 'kunateng',
               'luku', 'lukek', 'luki', 'kunaku', 'kunakek', 'kunaki']
    for ending in endings:
        if ending.startswith('l') and word.endswith('l' + ending):
            base = word[:-len(ending) - 1]
            if base.endswith('g') or base.endswith('r'):
                return base
            else:
                return base + 't'
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
        for left, right in ['()', '[]']:
            if left in center[:2]:
                start_pos = center.index(left)
                end_pos = center.index(right)
                combine_cons = center[:start_pos]
                vowel_ending = (before[-1:] in 'aeiou' or
                                (combine_cons == '-' and
                                 before[-2:].startswith('e')))
                if vowel_ending == (left == '('):
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


Widget = namedtuple('Table', ['id', 'title', 'rows', 'cols', 'spanrows', 'spancols'])
Widget.__new__.__defaults__ = ([], [], [])

HIERARCHY = {
    'n': [
        Widget(id='case-number', title='Case/Number',
               rows=[('ABS', 'normal'),
                     ('LOC', 'in'),
                     ('DAT', 'to'),
                     ('ABL', 'from'),
                     ('PER', 'through'),
                     ('SIM', 'like'),
                     ('ERG', 'possessive')],
               cols=[('SG', '1'),
                     ('DU', '2'),
                     ('PL', '3+')]),
        Widget(id='possessor', title='Possessor',
               rows=[('UNPOSS', '-'),
                     ('POSS1P', 'gui'),
                     ('POSS2P', 'ellpet'),
                     ('POSS3P', 'taugna')],
               cols=[('POSSSG', '1'),
                     ('POSSDU', '2'),
                     ('POSSPL', '3+')],
               spancols=['UNPOSS']),
    ],
    'vi': [
        Widget(id='tense', title='Tense',
               rows=[('PRES', 'present'),
                     ('PAST', 'past'),
                     ('CONJ', 'conjunctive'),
                     ('DEP', 'dependent')]),
        Widget(id='subject', title='Subject',
               rows=[('1P', 'gui'),
                     ('2P', 'ellpet'),
                     ('3P', 'taugna'),
                     ('4P', 'ellmenek')],
               cols=[('SG', '1'),
                     ('DU', '2'),
                     ('PL', '3+')]),
    ],
    'vt': [
        Widget(id='tense', title='Tense',
               rows=[('PRES', 'present'),
                     ('PAST', 'past'),
                     ('CONJ', 'conjunctive'),
                     ('DEP', 'dependent')]),
        Widget(id='subject', title='Subject',
               rows=[('S1P', 'gui'),
                     ('S2P', 'ellpet'),
                     ('S3P', 'taugna'),
                     ('S4P', 'ellmenek')],
               cols=[('SSG', '1'),
                     ('SDU', '2'),
                     ('SPL', '3+')]),
        Widget(id='object', title='Object',
               rows=[('O1P', 'gui'),
                     ('O2P', 'ellpet'),
                     ('O3P', 'taugna'),
                     ('O4P', 'ellmenek')],
               cols=[('OSG', '1'),
                     ('ODU', '2'),
                     ('OPL', '3+')]),
    ],
}


def id_list(widget, direction):
    assert direction in ('r', 'c')
    pairs = widget.rows if direction == 'r' else widget.cols
    span = widget.spanrows if direction == 'r' else widget.spancols
    span_suffix = ('-' + ','.join(span)) if span else ''
    return [id + span_suffix for id, name in pairs]


ID_LISTS = {
    'n': [
        id_list(HIERARCHY['n'][0], 'r'),
        id_list(HIERARCHY['n'][1], 'r'),
        id_list(HIERARCHY['n'][1], 'c'),
        id_list(HIERARCHY['n'][0], 'c'),
    ],
    'vi': [
        id_list(HIERARCHY['vi'][0], 'r'),
        id_list(HIERARCHY['vi'][1], 'r'),
        id_list(HIERARCHY['vi'][1], 'c'),
    ],
    'vt': [
        id_list(HIERARCHY['vt'][0], 'r'),
        id_list(HIERARCHY['vt'][1], 'r'),
        id_list(HIERARCHY['vt'][1], 'c'),
        id_list(HIERARCHY['vt'][2], 'r'),
        id_list(HIERARCHY['vt'][2], 'c'),
    ],
}


Table = namedtuple('Table', ['id', 'title', 'column_headers', 'rows'])
TableRow = namedtuple('TableRow', ['id', 'header', 'cells'])
TableCell = namedtuple('TableCell', ['id', 'map'])


def build_tables(chunk):
    endings_map = get_endings_map(chunk.entry, chunk.pos)

    for w in HIERARCHY[chunk.pos]:
        column_headers = [header for id_, header in w.cols]
        table = Table(w.id, w.title, column_headers,
                      list(build_rows(w, endings_map)))
        yield table


def build_rows(widget, endings_map):
    for id, header in widget.rows:
        row = TableRow(id, header,
                       list(build_cells(id, widget.cols, endings_map)))
        yield row


def external_subset(full_id, internal):
    '''
    >>> external_subset('PAST+1P+DU', ['1P', 'DU'])
    'PAST'
    '''
    return '+'.join(sorted(set(full_id.split('+')) -
                           set(internal)))


def build_cells(row_id, cols, endings_map):
    if cols:
        for col_id, header_ in cols:
            sub_map = {
                external_subset(full_id, [row_id, col_id]): inflection
                for full_id, inflection in endings_map.iteritems()
                if set([row_id, col_id]).issubset(full_id.split('+'))
            }
            cell = TableCell('+'.join([row_id, col_id]), sub_map)
            yield cell
    else:
        sub_map = {
            external_subset(full_id, [row_id]): inflection
            for full_id, inflection in endings_map.iteritems()
            if row_id in full_id.split('+')
        }
        cell = TableCell(row_id, sub_map)
        yield cell


def get_endings_map(entry, pos):
    '''
    >>> get_endings_map('yaamaq', 'n')['ABS+PL+UNPOSS']
    'yaamat'
    >>> get_endings_map('yaamaq', 'n')['ABS+DU+POSS1P+POSSSG']
    'yaamagka'
    >>> get_endings_map('silugluni', 'vi')['1P+PL+PRES']
    'silugtukut'
    >>> get_endings_map('nalluluku', 'vt')['O3P+OSG+PAST+S1P+SSG']
    "nalluk'gka"
    '''
    endings_map = {}
    build_endings(endings_map, ID_LISTS[pos], entry, ENDINGS[pos])
    return endings_map


def spanned(id_list, id_curr):
    '''
    >>> spanned(['B'], ['A'])
    False
    >>> spanned(['B-A'], ['A'])
    True
    >>> spanned(['B-A+C'], ['A'])
    False
    >>> spanned(['B-A+C'], ['A', 'C', 'E'])
    True
    >>> spanned(['B-A+D,C+D'], ['A', 'C', 'E'])
    False
    >>> spanned(['B-A+D,C+E'], ['A', 'C', 'E'])
    True
    '''
    if not id_list:
        return True
    id = id_list[0]
    if '-' not in id:
        return False

    id_curr = set(id_curr)

    conds = [set(cond.split('+')) for cond in id.split('-')[1].split(',')]
    return any(c.issubset(id_curr) for c in conds)


def build_endings(endings_map, id_lists, entry, endings, id_curr=None):
    '''
    >>> TEST_ENDINGS = [['+a', '+b'], ['+A', '+B']]
    >>> TEST_ID_LISTS = [['LOWER', 'UPPER'], ['A', 'B']]
    >>> result = {}
    >>> build_endings(result, TEST_ID_LISTS, 'x', TEST_ENDINGS)
    >>> result['B+LOWER']
    'xb'
    '''
    if id_curr == None:
        id_curr = []

    if id_lists:
        curr_list = id_lists[0]
        if spanned(curr_list, id_curr):
            build_endings(endings_map, id_lists[1:], entry,
                          endings, id_curr=id_curr)
        else:
            for id, sub_endings in zip(curr_list, endings):
                if '-' in id:
                    id = id.split('-')[0]
                build_endings(endings_map, id_lists[1:], entry,
                              sub_endings, id_curr=id_curr + [id])
    else:
        full_id = '+'.join(sorted(id_curr))
        cell = '-' if endings == '-' else morpho_join([entry, endings])
        endings_map[full_id] = cell



ENDINGS = {
    'n': [
        [
            ['~k', '-k', '-t'],
            [
                ['~ka', '-gka', '-nka'],
                ['~gpuk', '-puk', '-puk'],
                ['~gpet', '-pet', '-pet'],
            ],
            [
                ['-n', '-gken', '-ten'],
                ['~gtek', '-tek', '-tek'],
                ['~gci', '-ci', '-ci'],
            ],
            [
                ['-(~g)a', '-(~g)ak', '-(~ga)i'],
                ['-(~g)ak', '-(~ga)ik', '-(~ga)ik'],
                ['-(~g)at', '-(~ga)it', '-(~ga)it'],
            ],
        ]] + [
        [
            ['-men', '-nun', '-nun'] if ending == 'nun' else
            ['-gun', '-gun',  '-tgun'] if ending == 'kun' else
            ["-t'stun"] * 3 if ending == "t'stun" else
            ['-m' + ending[1:], '-' + ending, '-' + ending],
            [
                ['-m' + ending] * 3,
                ['-mteg' + ending] * 3,
                ['-mte' + ending] * 3,
            ],
            [
                ["~gp'" + ending] * 3,
                ["~gp'teg" + ending] * 3,
                ["~gp't's" + ending] * 3,
            ],
            [
                ['-(~g)a' + ending, '-(~ga)i' + ending, '-(~ga)i' + ending],
                ['-(~g)ag' + ending, '-(~ga)ig' + ending, '-(~ga)ig' + ending],
                ['-(~g)at' + ending, '-(~ga)it' + ending, '-(~ga)it' + ending],
            ],
        ] for ending in ['ni', 'nun', 'nek', 'kun', "t'stun"]] + [
        [
            ["-m", "-k", "-t"],
            [
                ["-ma", "-ma", "-ma"],
                ["-mnuk", "-mnuk", "-mnuk"],
                ["-mta", "-mta", "-mta"],
            ],
            [
                ["-gpet", "-gpet", "-gpet"],
                ["-gp'tek", "-gp'tek", "-gp'tek"],
                ["-gp'ci", "-gp'ci", "-gp'ci"],
            ],
            [
                ["-n", "-(~ga)ini", "-(~ga)ini"],
                ["-gta", "-(~ga)igta", "-(~ga)igta"],
                ["-ta", "-(~ga)ita", "-(~ga)ita"],
            ],
        ]
    ],
    'vi': [
        [
            ['+(+g)[+t]ua', '+[+t]ukuk', '+[+t]ukut'],
            ['+[+t]uten', '+[+t]utek', '+[+t]uci'],
            ['+[+t]uq', '+[+t]uk', '+[+t]ut'],
            ['-'] * 3,
        ],
        [
            ['-llrianga', '-llriakuk', '-llriakut'],
            ['-llriaten', '-llriatek', '-llriaci'],
            ['-llria', '-llriik', '-llriit'],
            ['-'] * 3,
        ],
        [
            ['~lua(nga)', '~lunuk', '~luta'],
            ['~luten', '~lutek', '~luci'],
            ['~luni', '~lutek', '~luteng'],
            ['-'] * 3,
        ],
        [
            ['~kuma', '~kumnuk', '~kumta'],
            ['~kut', '~kumtek', '~kumci'],
            ['~kan', '~kagta', '~kata'],
            ['~kuni', '~kunek', '~kuneng'],
        ],
    ],
    'vt': [
        [
            [
                [
                    ['-'] * 4,
                    ['+amken', '+amtek', '+amci'],
                    ['+aqa', '+agka', '+anka'],
                    ['-'] * 4,
                ],
                [
                    ['-'] * 4,
                    ['+amken', '+amtek', '+amci'],
                    ['+agpuk', '+apuk', '+apuk'],
                    ['-'] * 4,
                ],
                [
                    ['-'] * 4,
                    ['+amken', '+amtek', '+amci'],
                    ['+agpet', '+apet', '+apet'],
                    ['-'] * 4,
                ],
                [['-'] * 4] * 4,
            ],
            [
                [
                    ["+agp'nga", "+agp'kuk", "+agp'kut"],
                    ['-'] * 4,
                    ['+an', '+agken', '+aten'],
                    ['-'] * 4,
                ],
                [
                    ["+agp'tegennga", "+agp't'kuk", "+agp't'kut"],
                    ['-'] * 4,
                    ['+agtek', '+atek', '+atek'],
                    ['-'] * 4,
                ],
                [
                    ["+agp'cia", "+agp'cikuk", "+agp'cikut"],
                    ['-'] * 4,
                    ['+agci', '+aci', '+aci'],
                    ['-'] * 4,
                ],
                [['-'] * 4] * 4,
            ],
            [
                [
                    ['+aanga', '+aakuk', '+aakut'],
                    ['+aaten', '+aatek', '+aaci'],
                    ['+aa', '+ak', '+ai'],
                    ['-'] * 4,
                ],
                [
                    ['+aagnga', '+aigkuk', '+aigkut'],
                    ['+aagten', '+aigtek', "+ait'si"],
                    ['+aak', '+aik', '+aik'],
                    ['-'] * 4,
                ],
                [
                    ['+aatnga', '+aitkuk', '+aitkut'],
                    ['+aaten', "+ait'ek", "+ait'si"],
                    ['+aat', '+ait', '+ait'],
                    ['-'] * 4,
                ],
                [['-'] * 4] * 4,
            ],
        ],
        [
            [
                [
                    ['-'] * 4,
                    ['~kemken', '~kemtek', '~kemci'],
                    ["~k'gka", "~k'gka", '~kenka'],
                    ['-'] * 4,
                ],
                [
                    ['-'] * 4,
                    ['~kemken', '~kemtek', '~kemci'],
                    ["~k'gpuk", "~k'puk", "~k'puk"],
                    ['-'] * 4,
                ],
                [
                    ['-'] * 4,
                    ['~kemken', '~kemtek', '~kemci'],
                    ["~k'gpet", "~k'pet", "~k'pet"],
                    ['-'] * 4,
                ],
                [['-'] * 4] * 4,
            ],
            [
                [
                    ["~kugnga", "~kugkuk", "~kugkut"],
                    ['-'] * 4,
                    ['~ken', '~kegken', "~k'ten"],
                    ['-'] * 4,
                ],
                [
                    ["~kugt'gennga", "~kugt'kuk", "~kugt'kut"],
                    ['-'] * 4,
                    ["~k'gtek", "~k'tek", "~k'tek"],
                    ['-'] * 4,
                ],
                [
                    ["~kugcia", "~kugcikuk", "~kugcikut"],
                    ['-'] * 4,
                    ["~k'gci", "~k'ci", "~k'ci"],
                    ['-'] * 4,
                ],
                [['-'] * 4] * 4,
            ],
            [
                [
                    ['~kiinga', '~kiikuk', '~kiikut'],
                    ['~kiiten', '~kiitek', '~kiici'],
                    ['~kii', "~kek", '~kai'],
                    ['-'] * 4,
                ],
                [
                    ['~kiignga', '~kaigkuk', '~kaigkut'],
                    ['~kiigten', '~kaigtek', "~kait'si"],
                    ['~kiik', '~kaik', '~kaik'],
                    ['-'] * 4,
                ],
                [
                    ['~kiitnga', '~kaitkuk', '~kaitkut'],
                    ['~kiiten', "~kait'ek", "~kait'si"],
                    ['~kiit', '~kait', '~kait'],
                    ['-'] * 4,
                ],
                [['-'] * 4] * 4,
            ],
            [[['-'] * 4] * 4] * 4,
        ],
    ] * 2,
}

def inflection_data(chunk):
    if chunk.pos in ENDINGS:
        return {'inflections': inflect(chunk)}
    else:
        return {'inflections': None}


def inflect(chunk):
    '''
    return [build_table(s, column_headers,
            [TableRow(rh, ['-' if c == '-' else morpho_join([entry, c])
                           for c in row])
             for rh, row in zip(row_headers, cells[i])])
            for i, s in enumerate(HIERARCHY[chunk.pos])]
    '''
    return list(build_tables(chunk))
