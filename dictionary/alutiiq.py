import re
from collections import namedtuple


def get_root(word):
    endings = ['luni', 'lutek', 'luteng', 'kunani', 'kunatek', 'kunateng',
               'luku', 'lukek', 'luki', 'kunaku', 'kunakek', 'kunaki']
    for ending in endings:
        if ending.startswith('l') and word.endswith('l' + ending):
            base = word[:-len(ending) - 1]
            if base.endswith('r'):
                return base + base[-1]
            elif base[-1:] in 'qk':
                return base
            else:
                return base + 't'
        if ending.startswith('k') and word.endswith('g' + ending):
            return word[:-len(ending) - 1]
        if word.endswith(ending):
            if re.search('^([^aeiou]?)[aeiou][gr]$', word[:-len(ending)]):
                return word[:-len(ending)] + "'"
            elif word[:-len(ending)].endswith('ng'):
                return word[:-len(ending)] + 'e'
            else:
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
        for left, right in ['<>', '[]']:
            if left in center:
                start_pos = center.index(left)
                end_pos = center.index(right)
                combine_cons = center[:start_pos]
                vowel_ending = (before[-1:] in 'aiou' or
                                (combine_cons == '-' and
                                 before[-2:].startswith('e')))
                cons_ending = before[-1:] in 'rg'
                if left == '<' and vowel_ending or left =='[' and cons_ending:
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
            if center.endswith('rr') or center.endswith('gg'):
                center = center[:-2]
            elif center[-1] not in 'aeiou':
                center = center[:-1]
            elif center.endswith('e') and len(after) >= 2 and after[1] in 'aeiou':
                center = center[:-1] + "'"
        elif after.startswith('~'):
            center = get_root(center)
            if after.startswith('~k'):
                if center.endswith('t'):
                    if len(center) >= 2 and center[-2] not in 'aeiou':
                        center = center[:-1] + "'s"
                    else:
                        center = center[:-1] + 's'
                elif center[-1] not in 'aiou':
                    center = center[:-1]
            elif after.startswith('~g'):
                if center[-1] not in 'aeiou':
                    center = center[:-1]
            elif after.startswith('~l'):
                center = get_root(center)
                if center[-1] in "t'":
                    center = center[:-1]
            elif after[:2] in ('~a', '~i', '~u'):
                center = get_root(center)
                if center[-1:] == after[1]:
                    center += "'"
                elif center.endswith('e'):
                    center = center[:-1]
                elif center.endswith('i'):
                    center += 'y'
                elif center.endswith('u'):
                    center += 'w'
        elif after.startswith('+'):
            center = get_root(center)
            if center.endswith('e') and len(after) >= 2 and after[1] in 'aeiou':
                center = center[:-1]
            elif center.endswith("'") and len(after) >= 2 and after[1] not in 'aeiou':
                center = center[:-1]

        if re.search("[aeiou][aeiou]$", center) and \
                len(after) >= 2 and after[1] in 'aeiou':
            if center[-1:] == after[1]:
                center += "'"
            elif center.endswith('i') and after.startswith('~'):
                center += 'y'
            elif center.endswith('u') and after.startswith('~'):
                center += 'w'
            else:
                center += "'"

    if center.endswith('rr') or center.endswith('gg'):
        center = center[:-1]

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
            if (before[-1:] in 'qkt' or
                before.endswith('gg') or
                before.endswith('rr') or
                (len(before) >= 2 and before[-2] in 'aeiou' and before.endswith('t'))):
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


Widget = namedtuple('Table', ['id', 'title', 'default', 'rows', 'cols',
                              'spanrows', 'spancols', 'row_flatten', 'col_flatten'])
Widget.__new__.__defaults__ = ([], [], [], [], [])

HIERARCHY = {
    'n': [
        Widget(id='case-number', title='Case/Number',
               default='ABS:SG',
               rows=[('ABS', 'normal'),
                     ('ERG', 'subj/poss'),
                     ('LOC', 'at'),
                     ('DAT', 'to'),
                     ('ABL', 'from'),
                     ('PER', 'through'),
                     ('SIM', 'like')],
               cols=[('SG', '1'),
                     ('DU', '2'),
                     ('PL', '3+')]),
        Widget(id='possessor', title='Possessor',
               default='UNPOSS:POSSSG',
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
               default='PRES',
               rows=[('PRES', 'present'),
                     ('PAST', 'past'),
                     ('CONJ', 'conjunctive'),
                     ('DEP', 'dependent')]),
        Widget(id='subject', title='Subject',
               default='1P:SG',
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
               default='PRES',
               rows=[('PRES', 'present'),
                     ('PAST', 'past'),
                     ('CONJ', 'conjunctive'),
                     ('DEP', 'dependent')]),
        Widget(id='subject', title='Subject',
               default='S1P:SSG',
               rows=[('S1P', 'gui'),
                     ('S2P', 'ellpet'),
                     ('S3P', 'taugna'),
                     ('S4P', 'ellmenek')],
               cols=[('SSG', '1'),
                     ('SDU', '2'),
                     ('SPL', '3+')],
               row_flatten=['CONJ'],
               col_flatten=['CONJ']),
        Widget(id='object', title='Object',
               default='O3P:OSG',
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
    span = (widget.spanrows + widget.row_flatten) if direction == 'r' \
           else (widget.spancols + widget.col_flatten)
    span_suffix = ('-' + '_'.join(span)) if span else ''
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


Table = namedtuple('Table', ['id', 'title', 'default', 'column_headers',
                             'rows', 'row_span', 'col_span', 'collapse'])
TableRow = namedtuple('TableRow', ['header', 'cells'])
TableCell = namedtuple('TableCell', ['id', 'map'])


def build_tables(chunk):
    endings_map = get_endings_map(chunk.entry, chunk.pos)

    for w in HIERARCHY[chunk.pos]:
        column_headers = [header for id_, header in w.cols]
        table = Table(w.id, w.title, w.default, column_headers,
                      list(build_rows(w, endings_map)),
                      row_span={}, col_span={}, collapse={})

        for row_num, row in enumerate(table.rows):
            for col_num, cell in enumerate(row.cells):
                col_registry = (table.col_span if col_num == 0 else table.collapse)
                row_registry = (table.row_span if row_num == 0 else table.collapse)

                if cell.id.split(':')[0] in w.spancols:
                    col_registry[cell.id] = '*'
                elif w.col_flatten:
                    col_registry[cell.id] = '_'.join(w.col_flatten)

                if ':' in cell.id and cell.id.split(':')[1] in w.spanrows:
                    row_registry[cell.id] = '*'
                elif w.row_flatten:
                    row_registry[cell.id] = '_'.join(w.row_flatten)

        yield table


def build_rows(widget, endings_map):
    for id, header in widget.rows:
        row = TableRow(header,
                       list(build_cells(id, widget, endings_map)))
        yield row


def external_subset(full_id, internal):
    '''
    >>> external_subset('PAST:1P:DU', ['1P', 'DU'])
    'PAST'
    '''
    return ':'.join(sorted(set(full_id.split(':')) -
                           set(internal)))


def is_active(row_id, col_id, full_id, widget):
    '''
    >>> w = Widget(id='', title='', default='a:A',
    ...            rows=[('a', ''), ('b', '')],
    ...            cols=[('A', ''), ('B', '')],
    ...            row_flatten=['X'],
    ...            col_flatten=['X'])
    >>> is_active('a', 'B', 'a:B:Y', w)
    True
    >>> is_active('a', 'B', 'a:A:Y', w)
    False
    >>> is_active('a', 'B', 'X', w)
    True
    '''
    check_active = set()
    full_parts = set(full_id.split(':'))
    if row_id not in widget.spancols and \
            len(full_parts.intersection(widget.col_flatten)) == 0:
        check_active.add(col_id)
    if col_id not in widget.spanrows and \
            len(full_parts.intersection(widget.row_flatten)) == 0:
        check_active.add(row_id)
    return check_active.issubset(full_parts)


def build_cells(row_id, widget, endings_map):
    if widget.cols:
        for col_id, header_ in widget.cols:
            sub_map = {
                external_subset(full_id, [row_id, col_id]): inflection
                for full_id, inflection in endings_map.iteritems()
                if is_active(row_id, col_id, full_id, widget)
            }
            cell = TableCell(':'.join([row_id, col_id]), sub_map)
            yield cell
    else:
        sub_map = {
            external_subset(full_id, [row_id]): inflection
            for full_id, inflection in endings_map.iteritems()
            if row_id in full_id.split(':')
        }
        cell = TableCell(row_id, sub_map)
        yield cell


def get_endings_map(entry, pos):
    '''
    >>> get_endings_map('yaamaq', 'n')['ABS:PL:UNPOSS']
    'yaamat'
    >>> get_endings_map('yaamaq', 'n')['ABS:DU:POSS1P:POSSSG']
    'yaamagka'
    >>> get_endings_map('silugluni', 'vi')['1P:PL:PRES']
    'silugtukut'
    >>> get_endings_map("tang'rlluni", 'vi')['3P:CONJ:SG']
    "tang'rlluni"
    >>> get_endings_map("nerluni", 'vi')['3P:PRES:SG']
    "ner'uq"
    >>> get_endings_map("nerluni", 'vi')['3P:CONJ:SG']
    'nerluni'
    >>> get_endings_map("aqum'aluni", 'vi')['1P:PRES:SG']
    "aqum'agua(nga)"
    >>> get_endings_map('nalluluku', 'vt')['O3P:OSG:PRES:S1P:SSG']
    'nalluwaqa'
    >>> get_endings_map('aplluku', 'vt')['O3P:OSG:PRES:S1P:SSG']
    'aptaqa'
    >>> get_endings_map('eglluku', 'vt')['O3P:OSG:PRES:S1P:SSG']
    'egtaqa'
    >>> get_endings_map('aplluku', 'vt')['O3P:OSG:PAST:S1P:SSG']
    "ap'sk'gka"
    >>> get_endings_map('eglluku', 'vt')['O3P:OSG:PAST:S1P:SSG']
    "eg'sk'gka"
    >>> get_endings_map('qunuklluku', 'vt')['O3P:OSG:PRES:S1P:SSG']
    'qunukaqa'
    >>> get_endings_map('nalluluku', 'vt')['O3P:OSG:PAST:S1P:SSG']
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
    >>> spanned(['B-A:C'], ['A'])
    False
    >>> spanned(['B-A:C'], ['A', 'C', 'E'])
    True
    >>> spanned(['B-A:D_C:D'], ['A', 'C', 'E'])
    False
    >>> spanned(['B-A:D_C:E'], ['A', 'C', 'E'])
    True
    '''
    if not id_list:
        return True
    id = id_list[0]
    if '-' not in id:
        return False

    id_curr = set(id_curr)

    conds = [set(cond.split(':')) for cond in id.split('-')[1].split('_')]
    return any(c.issubset(id_curr) for c in conds)


def build_endings(endings_map, id_lists, entry, endings, id_curr=None):
    '''
    >>> TEST_ENDINGS = [['+a', '+b'], ['+A', '+B']]
    >>> TEST_ID_LISTS = [['LOWER', 'UPPER'], ['A', 'B']]
    >>> result = {}
    >>> build_endings(result, TEST_ID_LISTS, 'x', TEST_ENDINGS)
    >>> result['B:LOWER']
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
        full_id = ':'.join(sorted(id_curr))
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
                ['-<~g>a', '-<~g>k', '-<~g>i'],
                ['-<~g>ak', '-<~g>ik', '-<~g>ik'],
                ['-<~g>at', '-<~g>it', '-<~g>it'],
            ],
        ],
        [
            ["-m", "-k", "-t"],
            [
                ["-ma", "-ma", "-ma"],
                ["-mnuk", "-mnuk", "-mnuk"],
                ["-mta", "-mta", "-mta"],
            ],
            [
                ["~gpet", "~gpet", "~gpet"],
                ["~gp'tek", "~gp'tek", "~gp'tek"],
                ["~gp'ci", "~gp'ci", "~gp'ci"],
            ],
            [
                ["-n", "-<~g>ini", "-<~g>ini"],
                ["-gta", "-<~g>igta", "-<~g>igta"],
                ["-ta", "-<~g>ita", "-<~g>ita"],
            ],
        ],
        ] + [
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
                ['-<~g>a' + ending, '-<~g>i' + ending, '-<~g>i' + ending],
                ['-<~g>ag' + ending, '-<~g>ig' + ending, '-<~g>ig' + ending],
                ['-<~g>at' + ending, '-<~g>it' + ending, '-<~g>it' + ending],
            ],
        ] for ending in ['ni', 'nun', 'nek', 'kun', "t'stun"]
    ],
    'vi': [
        [
            ['~<+g>[+t]ua(nga)', '~[+t]ukuk', '~[+t]ukut'],
            ['~[+t]uten', '~[+t]utek', '~[+t]uci'],
            ['~[+t]uq', '~[+t]uk', '~[+t]ut'],
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
                    ['-'] * 3,
                    ['~amken', '~amtek', '~amci'],
                    ['~aqa', '~agka', '~anka'],
                    ['-'] * 3,
                ],
                [
                    ['-'] * 3,
                    ['~amken', '~amtek', '~amci'],
                    ['~arpuk', '~apuk', '~apuk'],
                    ['-'] * 3,
                ],
                [
                    ['-'] * 3,
                    ['~amken', '~amtek', '~amci'],
                    ['~arpet', '~apet', '~apet'],
                    ['-'] * 3,
                ],
            ],
            [
                [
                    ["~arp'nga", "~arp'kuk", "~arp'kut"],
                    ['-'] * 3,
                    ['~an', '~agken', '~aten'],
                    ['-'] * 3,
                ],
                [
                    ["~arp'tegennga", "~arp't'kuk", "~arp't'kut"],
                    ['-'] * 3,
                    ['~artek', '~atek', '~atek'],
                    ['-'] * 3,
                ],
                [
                    ["~arp'cia", "~arp'cikuk", "~arp'cikut"],
                    ['-'] * 3,
                    ['~arci', '~aci', '~aci'],
                    ['-'] * 3,
                ],
            ],
            [
                [
                    ['+<~g>aanga', '+<~g>aakuk', '+<~g>aakut'],
                    ['+<~g>aaten', '+<~g>aatek', '+<~g>aaci'],
                    ['+<~g>aa', '~ak', '+<~g>ai'],
                    ['-'] * 3,
                ],
                [
                    ['+<~g>aagnga', '+<~g>aigkuk', '+<~g>aigkut'],
                    ['+<~g>aagten', '+<~g>aigtek', "+<~g>ait'si"],
                    ['+<~g>aak', '+<~g>aik', '+<~g>aik'],
                    ['-'] * 3,
                ],
                [
                    ['+<~g>aatnga', '+<~g>aitkuk', '+<~g>aitkut'],
                    ['+<~g>aaten', "+<~g>ait'ek", "+<~g>ait'si"],
                    ['+<~g>aat', '+<~g>ait', '+<~g>ait'],
                    ['-'] * 3,
                ],
            ],
            [[['-'] * 3] * 4] * 3,
        ],
        [
            [
                [
                    ['-'] * 3,
                    ['~kemken', '~kemtek', '~kemci'],
                    ["~k'gka", "~k'gka", '~kenka'],
                    ['-'] * 3,
                ],
                [
                    ['-'] * 3,
                    ['~kemken', '~kemtek', '~kemci'],
                    ["~k'gpuk", "~k'puk", "~k'puk"],
                    ['-'] * 3,
                ],
                [
                    ['-'] * 3,
                    ['~kemken', '~kemtek', '~kemci'],
                    ["~k'gpet", "~k'pet", "~k'pet"],
                    ['-'] * 3,
                ],
            ],
            [
                [
                    ["~kugnga", "~kugkuk", "~kugkut"],
                    ['-'] * 3,
                    ['~ken', '~kegken', "~k'ten"],
                    ['-'] * 3,
                ],
                [
                    ["~kugt'gennga", "~kugt'kuk", "~kugt'kut"],
                    ['-'] * 3,
                    ["~k'gtek", "~k'tek", "~k'tek"],
                    ['-'] * 3,
                ],
                [
                    ["~kugcia", "~kugcikuk", "~kugcikut"],
                    ['-'] * 3,
                    ["~k'gci", "~k'ci", "~k'ci"],
                    ['-'] * 3,
                ],
            ],
            [
                [
                    ['~kiinga', '~kiikuk', '~kiikut'],
                    ['~kiiten', '~kiitek', '~kiici'],
                    ['~kii', "~kek", '~kai'],
                    ['-'] * 3,
                ],
                [
                    ['~kiignga', '~kaigkuk', '~kaigkut'],
                    ['~kiigten', '~kaigtek', "~kait'si"],
                    ['~kiik', '~kaik', '~kaik'],
                    ['-'] * 3,
                ],
                [
                    ['~kiitnga', '~kaitkuk', '~kaitkut'],
                    ['~kiiten', "~kait'ek", "~kait'si"],
                    ['~kiit', '~kait', '~kait'],
                    ['-'] * 3,
                ],
            ],
            [[['-'] * 3] * 4] * 3,
        ],
        [
            ['~lua(nga)', '~lunuk', '~luta', '-'],
            ['~luten', '~lutek', '~luci', '-'],
            ['~luku', '~lukek', '~luki', '-'],
            ['-'] * 4,
        ],
        [
            [
                [
                    ['-'] * 3,
                    ['~kumken', '~kumtek', '~kumci'],
                    ["~kumgu", "~kumkek", '~kumki'],
                    ["~kumni", "~kumtek", '~kumteng'],
                ],
                [
                    ['-'] * 3,
                    ['~kumken', '~kumtek', '~kumci'],
                    ["~kumt'gen'gu", "~kumt'gen'kek", "~kumt'gen'ki"],
                    ["~kumt'gni", "~kumt'gtek", "~kumt'gteng"],
                ],
                [
                    ['-'] * 3,
                    ['~kumken', '~kumtek', '~kumci'],
                    ["~kumt'gu", "~kumt'kek", "~kumt'ki"],
                    ["~kumt'ni", "~kumt'stek", "~kumt'steng"],
                ],
            ],
            [
                [
                    ["~kugnga", "~kugkuk", "~kugkut"],
                    ['-'] * 3,
                    ['~kugu', '~kugkek', "~kugki"],
                    ['~kugni', '~kugtek', "~kugteng"],
                ],
                [
                    ["~kugt'gennga", "~kugt'kuk", "~kugt'kut"],
                    ['-'] * 3,
                    ["~kugt'gengu", "~kugt'genkek", "~kugt'genki"],
                    ["~kugt'gni", "~kugt'gtek", "~kugt'gteng"],
                ],
                [
                    ["~kugcia", "~kugcikuk", "~kugcikut"],
                    ['-'] * 3,
                    ["~kugciu", "~kugcikek", "~kugciki"],
                    ["~kugt'sni", "~kugt'stek", "~kugt'steng"],
                ],
            ],
            [
                [
                    ['~kanga', '~kakuk', '~kakut'],
                    ['~katen', '~katek', '~kaci'],
                    ['~kagu', "~kakek", '~kaki'],
                    ['~kani', '~katek', "~kateng"],
                ],
                [
                    ['~kagnenga', '~kagnekuk', '~kagnekut'],
                    ['~kagten', '~kagtek', "~kagci"],
                    ['~kagnegu', "~kagnekek", '~kagneki'],
                    ['~kagni', '~kagtek', '~kagteng'],
                ],
                [
                    ['~katnga', '~katkuk', '~katkut'],
                    ['~katen', "~kat'ek", "~kat'si"],
                    ['~katgu', '~katkek', '~katki'],
                    ['~katni', "~kat'stek", "~kat'steng"],
                ],
            ],
            [
                [
                    ['~kunia', '~kunikuk', '~kunikut'],
                    ['~kuniten', '~kunitek', '~kunici'],
                    ['~kuniu', "~kunikek", '~kunikegki'],
                    ['-'] * 3,
                ],
                [
                    ["~kunegt'gennga", "~kunegt'genkuk", "~kunegt'genkut"],
                    ["~kunegt'gten", "~kunegt'gtek", "~kunegt'gci"],
                    ["~kunegt'gengu", "~kunegt'genkek", "~kunegt'genki"],
                    ['-'] * 3,
                ],
                [
                    ["~kunegt'nga", "~kunegt'kuk", "~kunegt'kut"],
                    ["~kunegt'sten", "~kunegt'stek", "~kunegt'si"],
                    ["~kunegt'gu", "~kunegt'kek", "~kunegt'ki"],
                    ['-'] * 3,
                ],
            ],
        ],
    ],
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
