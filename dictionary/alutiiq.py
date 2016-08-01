import re
from collections import namedtuple


def normalize(word):
    '''
    Perform fuzzy search normalization (collapse commonly confused sounds
    so search is resilient to misspellings of Alutiiq words).

    >>> normalize('tuumiaqlluku')
    'tumiaklluku'
    >>> normalize("Wiiwaq")
    'uiuak'
    >>> normalize("estui'isuun")
    'stuisun'
    '''
    word = re.subn(r'(?<!n)g', 'r', word)[0]
    word = re.subn(r'[A-QS-Z]', lambda m: m.group().lower(), word)[0]
    word = (word.replace('q', 'k')
                .replace('y', 'i')
                .replace('w', 'u')
                .replace('e', '')
                .replace("'", ''))
    for vowel in 'aiu':
        word = re.sub(vowel + '+', vowel, word)
    return word


CONSONANT = '([ptckqwlysgrmnR]|gw|ng|ll|hm|hn|hng)'
ONSET = '(' + CONSONANT + "|')"
PRIME = '[aiu]'
CORE = "([e']|" + PRIME + '{1,2})'
RHYME = '(' + CORE + '([ptkqlsgrmn]|ng|ll)?)'
GEMINATE = '(' + CONSONANT + "')"
VALID_REGEX = re.compile('^' + CONSONANT + '?' +
                         '(' + RHYME + ONSET + '|' +
                         CORE + GEMINATE + ')*' +
                         RHYME +
                         '$')


def is_valid(entry):
    '''
    >>> is_valid('pingayun')
    True
    >>> is_valid('piyngayun')
    False
    >>> is_valid('Pingayiin')
    True
    >>> is_valid('Eengayiin')
    False
    >>> is_valid('alIa')
    False
    '''
    words = entry.split()
    return all(VALID_REGEX.match(w[0].lower() + w[1:])
               for w in words)


def get_pos(entry, defn=''):
    if any(entry.endswith(marker + ending)
           for marker in ["lu", "l'u", "na"]
           for ending in ['ni', 'tek', 'teng']):
        return 'vi'
    elif any(entry.endswith(marker + ending)
             for marker in ["lu", "l'u", "na"]
             for ending in ['ku', 'kek', 'ki']):
        return 'vt'
    elif entry and entry[-1:] in 'qkt':
        return 'n'
    else:
        return 'None'


def get_root(word, defn=''):
    markers = ["lu", "l'u", "kuna"]
    finals = ['ni', 'tek', 'teng', 'ku', 'kek', 'ki']
    for marker in markers:
        for final in finals:
            ending = marker + final
            if ending.startswith('l') and word.endswith('l' + ending):
                base = word[:-len(ending) - 1]
                if "'" in ending:
                    return base + "t'e"
                elif base.endswith('r'):
                    return base + base[-1]
                elif base[-1:] in 'qk':
                    return base + 'e'
                elif len(base) >= 2 and base[-2] == base[-1]:
                    return base[:-1] + '\\' + base[-1] + 'te'
                else:
                    return base + 'te'
            if marker == 'kuna' and word.endswith('g' + ending):
                return word[:-len(ending) - 1] + 'N'
            if word.endswith(ending):
                if "'" in marker:
                    return word[:-len(ending)] + "le"
                elif marker == 'kuna':
                    return word[:-len(ending)] + 'N'
                elif re.search('^([^aeiou]?)[aeiou][gr]$', word[:-len(ending)]):
                    return word[:-len(ending)] + "e"
                elif word[:-len(ending)].endswith('ng'):
                    return word[:-len(ending)] + 'e'
                else:
                    return word[:-len(ending)]

    neg_endings = ['nani', 'natek', 'nateng', 'naku', 'nakek', 'naki']
    for ending in neg_endings:
        if word.endswith('ii' + ending):
            return word[:-len(ending) - 1] + '\iT'
        elif word.endswith(ending):
            return word[:-len(ending)] + 'T'

    if re.search('(^|[^aeiou])[aeiou]teq$', word):
        return word[:-1] + 'r'
    elif re.search('^[^aeiou]?[aeiou][qk]$', word):
        return word[:-1] + '\\' + word[-2] + ('r' if word[-1] == 'q' else 'g')
    elif word.endswith('ta') or word.endswith('na'):
        return word[:-1] + 'A'
    elif word.endswith('teq'):
        return word[:-1]
    elif word.endswith('q'):
        return word[:-1] + 'r'
    elif word.endswith('k'):
        return word[:-1] + 'g'
    elif word.endswith('ani'):
        return word[:-3] + 'r'
    elif word.endswith('iini'):
        return word[:-4] + 'A'
    elif word.endswith('iitni'):
        return word[:-5] + 'A'
    elif word.endswith('gpeni'):
        return word[:-5]
    elif word.endswith('a'):
        return word[:-1] + 'r'
    elif word.endswith('ii'):
        return word[:-2] + 'A'
    elif word.endswith('iit'):
        return word[:-3] + 'A'

    return word


def apply_vowel_alternation(center, before):
    if center is None:
        return None

    if before is not None:
        before = get_root(before)
        for left, right in ['<>', '[]', '{}']:
            if left in center:
                start_pos = center.index(left)
                end_pos = center.index(right)
                combine_cons = center[:start_pos]
                vowel_ending = (before[-1:] in 'aiou' or
                                (combine_cons == '-' and
                                 before[-2:-1] in list('Ae')))
                cons_ending = before[-1:] in 'rg' or before.endswith('ll')
                strong_fric_ending = (before[-1:] == 'g' or
                                      before.endswith('er'))
                if (left == '<' and vowel_ending or
                        left == '[' and cons_ending or
                        left == '{' and strong_fric_ending):
                    center = center[start_pos + 1:end_pos] + center[end_pos + 1:]
                else:
                    center = center[:start_pos] + center[end_pos + 1:]

    return center


def apply_negative(before, center):
    if before is not None and center is not None:
        negative = False

        if center.startswith('!'):
            # negative root + negative postbase = positive
            center = center[1:]
            if before.endswith('N'):
                # nalluN !~aqa => nallu ~aqa => nalluwaqa
                before = before[:-1]
            elif before.endswith('T'):
                # asiI !+[+t]uq => asir +[+t]uq => asirtuq
                if before.endswith(r'\iT'):
                    before = before[:-3] + 'r'
                elif re.search(r'[au]iT$', before):
                    before = before[:-2] + 'r'
                elif before.endswith('kiT'):
                    before = before[:-3] + "tu"
                elif re.search(r'[aeiou]T$', before):
                    before = before[:-1]
                    negative = True
                else:
                    before = before[:-1] + 'e'
                    negative = True
            elif before.endswith('iX'):
                # piiX !+[+t]uq => pinq'rr !+[+t]uq => pingq'rtuq
                before = before[:-2] + "ngq'rr"
            else:
                negative = True
        elif before[-1:] in 'NTX':
            negative = True

        if negative:
            if center.startswith('~a') or center.startswith('+<~g>a') or \
                    '[+t]u' in center:
                # present tense:
                #   transitive (not third person): ~a
                #   transitive third person: +<~g>a
                #   intransitive: ...[+t]u
                # nalluN ~aqa => nallun'ite ~aqa => nallun'itaqa
                pass
            elif center.startswith('~lu'):
                # nallu !~luku => nallu +g[~]kunaku => nallugkunaku
                center = "+na" + center[3:]
                if center.endswith('naten'):
                    # nallu !~luten => nallu +g[~]kunak => nallugkunak
                    center = center[:-5] + 'nak'
                else:
                    # nallu !~lua(nga) => nallu +g[~]kunii(nga) => nallugkunii(nga)
                    center = center.replace('naa', 'nii')
            elif center.startswith('-llr'):
                # nallu !-llria => nallune -lnge +[+t]uq => nallunilnguq
                center = morpho_join(["~lnge", PAST_MAP[center]])
            elif center.startswith('~ng'):
                # nallu !~ngama => nallun'te ~lngama => nallun'llngama
                # asiI ~ngama => asi\i ~lngama => asiilngama
                center = '~' + morpho_join(["l", center])
            else:
                # nallu !~k'gka => nallun'te ~llk'gka => nallun'llk'gka
                # also -kuma, question endings (need to check those)
                center = '~' + morpho_join(["ll", center])

        # negative root + positive postbase = negative
        if before.endswith('iT') or before.endswith('iX'):
            # asi\iT +[+t]uq => asi\i +tuq => asiituq
            # pi\iX +[+t]uq => pi\i +tuq => piituq
            before = before[:-1]
            if not center.startswith('~l') and not center.startswith('+n'):
                before += 'te'
        elif before.endswith('T'):
            # mikT +[+t]uq => mikt +uq => miktuq
            before = before[:-1] + 'te'
        elif negative:
            if before.endswith('N'):
                before = before[:-1]

            if before.endswith('tu'):
                # agatuN ~luni => agaki +nani => agakinani
                before = before[:-2] + 'ki'
            elif center.startswith('+n'):
                # nalluN ~luku => nallu +g[~]kunaku => nallugkunaku
                center = '+g[~]kun' + center[len('+n'):]
            elif center.startswith('~lngu'):
                # nalluN ~llria => nalluni ~lnguq => nallunilnguq
                before = morpho_join([before, "-ni"])
            elif center.startswith('~l'):
                # nalluN ~kuma => nallun'te ~lkuma => nallun'llkuma
                before = morpho_join([before, "-n'te"])
            else:
                # nalluN ~aqa => nallune -itaqa => nallun'itaqa
                before = morpho_join([before, "-n'ite"])

    return before, center


def apply_transformations(before, center, after):
    before, center = apply_negative(before, center)
    center, after = apply_negative(center, after)
    center = apply_vowel_alternation(center, before)
    after = apply_vowel_alternation(after, center)

    if after is not None:
        if after.startswith('-'):
            if center.endswith('A'):
                if after[:2] == '-a':
                    center = center[:-1] + 'i'
                elif after[:2] == '-i':
                    center = center[:-1] + 'a'
                else:
                    # akulA +a => akulii
                    center = center[:-1] + 'e'
            if center.endswith('rr') or center.endswith('gg'):
                center = center[:-2]
            elif center[-1] not in 'aeiou':
                center = center[:-1]
            elif center.endswith("t'e"):
                center = center[:-1]
            elif center.endswith('e') and len(after) >= 2 and after[1] in 'aeiou':
                center = center[:-1] + "'"
        elif after.startswith('~'):
            if after.startswith('~k'):
                if center.endswith('A') and after == '~k':
                    # piugtA ~k => piugta
                    center = center[:-1] + 'a'
                elif center.endswith('A'):
                    # piugtA ~ka => piugteka
                    center = center[:-1] + 'e'

                if center.endswith("t'e"):
                    center = center[:-3] + 'll'
                elif center.endswith('te'):
                    if len(center) >= 3 and center[-3] not in 'aeiou':
                        center = center[:-2] + "'s"
                    else:
                        center = center[:-2] + 's'
                elif center.endswith('qe') or center.endswith('ke'):
                    center = center[:-1] + "'g"
                elif center.endswith('g') and len(after) >= 3 and after[2] in 'aeiou':
                    if center.endswith('gg'):
                        center = center[:-1]
                    # leave one g in place
                elif center.endswith('gg') or center.endswith('rr'):
                    center = center[:-2]
                elif center[-1] not in 'aioul':
                    center = center[:-1]
            elif after.startswith('~g'):
                if re.search('[aeiou]' + CONSONANT + 'e[gr]$', center) and \
                        len(after) >= 3 and after[2] in 'aeiou':
                    # nater ~ga => natra
                    center = center[:-2]
                elif center[-1] not in 'aeiou':
                    # yaamar ~gci => yaamarci
                    center = center[:-1]
            elif after.startswith('~l') or after.startswith('~ng'):
                if center.endswith("t'e"):
                    # et'e ~ngama => ellngama
                    center = center[:-3] + "ll"

                    if after.startswith('~l'):
                        # et'e ~luni => ell'uni
                        center += "'"
                elif center.endswith('te'):
                    # aiwite ~ngama => aiwicama
                    center = center[:-2]

                    if center and center[-1] not in "aeiou'":
                        # mikte ~lnguq => mik'llnguq
                        center += "'"
                elif after.startswith('~l') and center.endswith('le'):
                    # ule ~luni => ul'uni
                    center = center[:-1] + "'"
                elif center.endswith('e'):
                    # age ~luni => agluni
                    center = center[:-1]
            elif after[:2] in ('~a', '~i', '~u'):
                if center[-1:] == after[1]:
                    center += "'"
                elif center.endswith('e'):
                    center = center[:-1]
                elif center.endswith('i'):
                    center += 'y'
                elif center.endswith('u'):
                    center += 'w'
        elif after.startswith('+'):
            if center.endswith('e') and len(after) >= 2 and after[1] in 'aeiou':
                # qitenge +uq => qitenguq
                center = center[:-1]
                if (center.endswith('g') and not center.endswith('ng')) or \
                        center.endswith('r'):
                    # nere +uq => ner'uq
                    center += "'"
            elif center.endswith("'") and len(after) >= 2 and after[1] not in 'aeiou':
                center = center[:-1]
            elif re.search('[aeiou]' + CONSONANT + 'e[gr]$', center) and \
                    len(after) >= 2 and after[1] in 'aeiou':
                center = center[:-2] + center[-1]

        if re.search("[aeiou][aeiou]$", center) and \
                len(after) >= 2 and after[1] in 'aeiou':
            if center[-1:] == after[1]:
                center += "'"
            elif center.endswith('i'):
                center += 'y'
            elif center.endswith('u'):
                center += 'w'
            else:
                center += "'"

    if center.endswith('rr') or center.endswith('gg'):
        center = center[:-1]

    if before is not None:
        if center.startswith('~k'):
            if before.endswith('r'):
                # kayar ~k => kayaq
                # kayar ~ka => kayaqa
                # minar ~kii => minaqii
                center = 'q' + center[2:]
            elif before.endswith('A'):
                center = ''
            else:
                # nuteg ~k => nutek
                # nuteg ~ka => nutegka
                center = center[1:]
        elif center.startswith('~g'):
            if before.endswith('r'):
                center = 'r' + center[2:]
            else:
                center = center[1:]
        elif center.startswith('~l'):
            if (before[-2:] in ('qe', 'ke', 'te') or  # caqe ~luni => caqlluni
                    before.endswith('gg') or  # cupugg ~luni => cupuglluni
                    before.endswith('rr')):  # angq'rr ~luni => angq'rlluni
                center = center[1:]
                if not center.startswith('ll'):
                    center = 'l' + center
            elif before.endswith("t'e") or before.endswith("le"):
                center = center[2:]
            else:
                center = center[1:]
        elif center.startswith('~ng'):
            if before.endswith('te'):
                center = 'c' + center[3:]
            else:
                center = center[1:]
        elif center[0] in '+-~':
            center = center[1:]
            if center.startswith('a') and before.endswith('A'):
                center = 'i' + center[1:]
        else:
            center = ' ' + center

    if after and re.search(r'^.' + CONSONANT + "[aeiou']", after):
        # su\ug ~ka => sugka
        center = re.sub(r'([aiu])\\\1' + CONSONANT + '$', r'\1\2', center)
        # asi\i +tuq => asiituq
        center = re.sub(r'([aiu])\\([aiu])$', r'\1\2', center)
    elif after and re.search(r'^.' + CONSONANT + '(' + CONSONANT + '|$)', after):
        # su\ug ~k => suk
        # su\ug ~gci => sugci
        # pi\i +lnguq = pilnguq
        center = re.sub(r'([aiu])\\\1$', r'\1', center)
    elif after:
        # su\ug +a => suuga
        center = re.sub(r'(?<=[a-zR])\\(?=[aiu])', '', center)

    return center


def morpho_join(chunks):
    if '-' in chunks:
        return '-'

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
                     ('POSS3P', 'taugna'),
                     ('POSS4P', 'ellmenek')],
               cols=[('POSSSG', '1'),
                     ('POSSDU', '2'),
                     ('POSSPL', '3+')],
               spancols=['UNPOSS']),
    ],
    'vi': [
        Widget(id='tense', title='Tense',
               default='PRES:POS',
               rows=[('PRES', 'present'),
                     ('PAST', 'past'),
                     ('CONJ', 'conjunctive'),
                     ('INTERR', 'question'),
                     ('COND', 'if'),
                     ('CSEQ', 'when')],
               cols=[('POS', 'positive'),
                     ('NEG', 'negative')]),
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
               default='PRES:POS',
               rows=[('PRES', 'present'),
                     ('PAST', 'past'),
                     ('CONJ', 'conjunctive'),
                     ('INTERR', 'question'),
                     ('COND', 'if'),
                     ('CSEQ', 'when')],
               cols=[('POS', 'positive'),
                     ('NEG', 'negative')]),
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
    'loc': [
        Widget(id='case-number', title='Case/Number',
               default='ABS:SG',
               rows=[('ABS', 'normal'),
                     ('ERG', 'poss'),
                     ('LOC', 'at'),
                     ('DAT', 'to'),
                     ('ABL', 'from'),
                     ('PER', 'through')],
               cols=[('SG', '1'),
                     ('DU', '2'),
                     ('PL', '3+')]),
        Widget(id='possessor', title='Possessor',
               default='UNPOSS:POSSSG',
               rows=[('UNPOSS', '-'),
                     ('POSS1P', 'gui'),
                     ('POSS2P', 'ellpet'),
                     ('POSS3P', 'taugna'),
                     ('POSS4P', 'ellmenek')],
               cols=[('POSSSG', '1'),
                     ('POSSDU', '2'),
                     ('POSSPL', '3+')],
               spancols=['UNPOSS']),
    ],
}


def id_list(widget, direction):
    assert direction in ('r', 'c')
    pairs = widget.rows if direction == 'r' else widget.cols
    span = ((widget.spanrows + widget.row_flatten)
            if direction == 'r' else
            (widget.spancols + widget.col_flatten))
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
        id_list(HIERARCHY['vi'][0], 'c'),
        id_list(HIERARCHY['vi'][0], 'r'),
        id_list(HIERARCHY['vi'][1], 'r'),
        id_list(HIERARCHY['vi'][1], 'c'),
    ],
    'vt': [
        id_list(HIERARCHY['vt'][0], 'c'),
        id_list(HIERARCHY['vt'][0], 'r'),
        id_list(HIERARCHY['vt'][1], 'r'),
        id_list(HIERARCHY['vt'][1], 'c'),
        id_list(HIERARCHY['vt'][2], 'r'),
        id_list(HIERARCHY['vt'][2], 'c'),
    ],
    'loc': [
        id_list(HIERARCHY['loc'][0], 'r'),
        id_list(HIERARCHY['loc'][1], 'r'),
        id_list(HIERARCHY['loc'][1], 'c'),
        id_list(HIERARCHY['loc'][0], 'c'),
    ],
}


Table = namedtuple('Table', ['id', 'title', 'default', 'column_headers',
                             'rows', 'row_span', 'col_span', 'collapse'])
TableRow = namedtuple('TableRow', ['header', 'cells'])
TableCell = namedtuple('TableCell', ['id', 'map'])


def build_tables(root):
    endings_map = get_endings_map(root.root, root.pos)

    for w in HIERARCHY[root.pos]:
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


def get_endings_map(root, pos):
    '''
    >>> get_endings_map('yaamar', 'n')['ABS:DU:POSS1P:POSSSG']
    'yaamagka'
    >>> get_endings_map('silug', 'vi')['1P:PL:POS:PRES']
    'silugtukut'
    >>> get_endings_map('nallu', 'vt')['O3P:OSG:POS:PRES:S1P:SSG']
    'nalluwaqa'
    '''
    endings_map = {}
    build_endings(endings_map, ID_LISTS[pos], root, ENDINGS[pos])
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


def build_endings(endings_map, id_lists, root, endings, id_curr=None):
    '''
    >>> TEST_ENDINGS = [['+a', '+b'], ['+A', '+B']]
    >>> TEST_ID_LISTS = [['LOWER', 'UPPER'], ['A', 'B']]
    >>> result = {}
    >>> build_endings(result, TEST_ID_LISTS, 'x', TEST_ENDINGS)
    >>> result['B:LOWER']
    'xb'
    '''
    if id_curr is None:
        id_curr = []

    if id_lists:
        curr_list = id_lists[0]
        if spanned(curr_list, id_curr):
            build_endings(endings_map, id_lists[1:], root,
                          endings, id_curr=id_curr)
        else:
            for id, sub_endings in zip(curr_list, endings):
                if '-' in id:
                    id = id.split('-')[0]
                build_endings(endings_map, id_lists[1:], root,
                              sub_endings, id_curr=id_curr + [id])
    else:
        full_id = ':'.join(sorted(id_curr))
        cell = morpho_join([root, endings])
        endings_map[full_id] = cell


def negatives(table):
    if isinstance(table, list):
        return [negatives(r) for r in table]
    elif table == '-':
        return '-'
    else:
        return '!' + table


def add_negatives(table):
    return [table, negatives(table)]


def correspondences_map(table1, table2, result=None):
    if result is None:
        result = {}

    if isinstance(table1, list) and isinstance(table2, list):
        for sub1, sub2 in zip(table1, table2):
            correspondences_map(sub1, sub2, result)
    else:
        result[table1] = table2

    return result


VI_PRES = [
    ['+<+g>[+t]ua(nga)', '+[+t]ukuk', '+[+t]ukut'],
    ['+[+t]uten', '+[+t]utek', '+[+t]uci'],
    ['+[+t]uq', '+[+t]uk', '+[+t]ut'],
    ['-'] * 3,
]

VI_PAST = [
    ['-llrianga', '-llriakuk', '-llriakut'],
    ['-llriaten', '-llriatek', '-llriaci'],
    ['-llria', '-llriik', '-llriit'],
    ['-'] * 3,
]

PAST_MAP = correspondences_map(VI_PAST, VI_PRES)


ENDINGS = {
    'n': [
        [
            ['~k', '-{+e}k', '-{+e}t'],
            [
                ['~{~}ka', '-{+e}gka', '-{+e}nka'],
                ['~gpuk', '-{+}puk', '-{+}puk'],
                ['~gpet', '-{+}pet', '-{+}pet'],
            ],
            [
                ['-{+e}n', '-{+e}gken', '-{+e}ten'],
                ['~gtek', '-{+}tek', '-{+}tek'],
                ['~gci', '-{+}ci', '-{+}ci'],
            ],
            [
                ['-<~g>{+}a', '-<~g>{+e}k', '-<~g>{+}i'],
                ['-<~g>{+}ak', '-<~g>{+}ik', '-<~g>{+}ik'],
                ['-<~g>{+}at', '-<~g>{+}it', '-<~g>{+}it'],
            ],
            [
                ['-{+}ni', '-{+e}gni', '-{+}ni'],
                ['~gtek', '-{+}tek', '-{+}tek'],
                ['~gteng', '-{+}teng', '-{+}teng'],
            ],
        ],
        [
            ["-{+e}m", "-{+e}k", "-{+e}t"],
            [
                ["-{+}ma", "-{+e}gma", "-{+}ma"],
                ["-{+e}mnuk", "-{+e}mnuk", "-{+e}mnuk"],
                ["-{+e}mta", "-{+e}mta", "-{+e}mta"],
            ],
            [
                ["~gpet", "~gpet", "~gpet"],
                ["~gp'tek", "~gp'tek", "~gp'tek"],
                ["~gp'ci", "~gp'ci", "~gp'ci"],
            ],
            [
                ["-{+e}n", "-<~g>ini", "-<~g>ini"],
                ["-{+e}gta", "-<~g>igta", "-<~g>igta"],
                ["-{+}ta", "-<~g>ita", "-<~g>ita"],
            ],
            [
                ['-{+}mi', '-{+e}gni', '-{+}mi'],
                ['-{+}megtek', '-{+}megtek', '-{+}megtek'],
                ['-{+}megta', '-{+}megta', '-{+}megta'],
            ],
        ],
        ] + [
        [
            ['-{+}men', '-{+}nun', '-{+}nun'] if ending == 'nun' else
            ['-g{+k}un', '-g{+k}un',  '-tgun'] if ending == 'kun' else
            ["-{+}t'stun"] * 3 if ending == "t'stun" else
            ['-{+}m' + ending[1:], '-{+}' + ending, '-{+}' + ending],
            [
                ['-{+e}m' + ending] * 3,
                ['-{+e}mteg' + ending] * 3,
                ['-{+e}mt' + ("e" if ending == "t'stun" else "'") + ending] * 3,
            ],
            [
                ["~gp'" + ending] * 3,
                ["~gp'teg" + ending] * 3,
                ["~gp't's" + ('gun' if ending == 'kun' else ending)] * 3,
            ],
            [
                ['-<~g>a' + ending, '-<~g>i' + ending, '-<~g>i' + ending],
                ['-<~g>ag' + ending, '-<~g>ig' + ending, '-<~g>ig' + ending],
                ['-<~g>at' + ending, '-<~g>it' + ending, '-<~g>it' + ending],
            ],
            [
                ['-{+}mi' + ending] * 3,
                ['-{+}megteg' + ending] * 3,
                ["-{+}megt" + ("e" if ending == "t'stun" else "'") + ending] * 3,
            ],
        ] for ending in ['ni', 'nun', 'nek', 'kun', "t'stun"]
    ],
    'loc': [
        [
            ['~k', '-{+e}k', '-{+e}t'],
            [
                ['~{~}ka', '-{+e}gka', '-{+e}nka'],
                ['~gpuk', '-{+}puk', '-{+}puk'],
                ['~gpet', '-{+}pet', '-{+}pet'],
            ],
            [
                ['-{+e}n', '-{+e}gken', '-{+e}ten'],
                ['~gtek', '-{+}tek', '-{+}tek'],
                ['~gci', '-{+}ci', '-{+}ci'],
            ],
            [
                ['-<~g>{+}a', '-<~g>{+e}k', '-<~g>{+}i'],
                ['-<~g>{+}ak', '-<~g>{+}ik', '-<~g>{+}ik'],
                ['-<~g>{+}at', '-<~g>{+}it', '-<~g>{+}it'],
            ],
            [
                ['-{+}ni', '-{+e}gni', '-{+}ni'],
                ['~gtek', '-{+}tek', '-{+}tek'],
                ['~gteng', '-{+}teng', '-{+}teng'],
            ],
        ],
        [
            ["-{+e}m", "-{+e}k", "-{+e}t"],
            [
                ["-{+}ma", "-{+e}gma", "-{+}ma"],
                ["-{+e}mnuk", "-{+e}mnuk", "-{+e}mnuk"],
                ["-{+e}mta", "-{+e}mta", "-{+e}mta"],
            ],
            [
                ["~gpet", "~gpet", "~gpet"],
                ["~gp'tek", "~gp'tek", "~gp'tek"],
                ["~gp'ci", "~gp'ci", "~gp'ci"],
            ],
            [
                ["-{+e}n", "-<~g>ini", "-<~g>ini"],
                ["-{+e}gta", "-<~g>igta", "-<~g>igta"],
                ["-{+}ta", "-<~g>ita", "-<~g>ita"],
            ],
            [
                ['-{+}mi', '-{+e}gni', '-{+}mi'],
                ['-{+}megtek', '-{+}megtek', '-{+}megtek'],
                ['-{+}megta', '-{+}megta', '-{+}megta'],
            ],
        ],
        ] + [
        [
            ['-{+}men', '-{+}nun', '-{+}nun'] if ending == 'nun' else
            ['-g{+k}un', '-g{+k}un',  '-tgun'] if ending == 'kun' else
            ['-{+}m' + ending[1:], '-{+}' + ending, '-{+}' + ending],
            [
                ['-{+e}m' + ending] * 3,
                ['-{+e}mteg' + ending] * 3,
                ['-{+e}mt' + ("e" if ending == "t'stun" else "'") + ending] * 3,
            ],
            [
                ["~gp'" + ending] * 3,
                ["~gp'teg" + ending] * 3,
                ["~gp't's" + ('gun' if ending == 'kun' else ending)] * 3,
            ],
            [
                ['-<~g>a' + ending, '-<~g>i' + ending, '-<~g>i' + ending],
                ['-<~g>ag' + ending, '-<~g>ig' + ending, '-<~g>ig' + ending],
                ['-<~g>at' + ending, '-<~g>it' + ending, '-<~g>it' + ending],
            ],
            [
                ['-{+}mi' + ending] * 3,
                ['-{+}megteg' + ending] * 3,
                ["-{+}megt" + ("e" if ending == "t'stun" else "'") + ending] * 3,
            ],
        ] for ending in ['ni', 'nun', 'nek', 'kun', "t'stun"]
    ],
    'vi': add_negatives([
        VI_PRES,
        VI_PAST,
        [
            ['~lua(nga)', '~lunuk', '~luta'],
            ['~luten', '~lutek', '~luci'],
            ['~luni', '~lutek', '~luteng'],
            ['-'] * 3,
        ],
        [
            ['+<+s>[+ci]a', "+t'snuk", "+t'sta"],
            ["~[+c]it", "+t'stek", "+t'si"],
            ["~[+t]a", "~[+t]ak", "~[+t]at"],
            ['-'] * 3,
        ],
        [
            ['~kuma', '~kumnuk', '~kumta'],
            ['~kut', '~kumtek', '~kumci'],
            ['~kan', '~kagta', '~kata'],
            ['~kuni', '~kunek', '~kuneng'],
        ],
        [
            ['~ngama', '~ngamnuk', '~ngamta'],
            ['~ngaut', "~ngaugtek", "~ngaugci"],
            ['~ngan', '~ngagta', '~ngata'],
            ['~ngami', '~ngamek', '~ngameng'],
        ],
    ]),
    'vt': add_negatives([
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
                    ['+<+y>[+c]imken', '+<+y>[+c]imtek', '+<+y>[+c]imci'],
                    ['~[+t]aqa', '~[+t]agka', '~[+t]anka'],
                    ['-'] * 3,
                ],
                [
                    ['-'] * 3,
                    ['+<+y>[+c]imken', '+<+y>[+c]imtek', '+<+y>[+c]imci'],
                    ["+t'snuk"] * 3,
                    ['-'] * 3,
                ],
                [
                    ['-'] * 3,
                    ['+<+y>[+c]imken', '+<+y>[+c]imtek', '+<+y>[+c]imci'],
                    ["+t'sta"] * 3,
                    ['-'] * 3,
                ],
            ],
            [
                [
                    ["+<+y>[+ci]a", "+<+y>[+c]ikuk", "+<+y>[+c]ikut"],
                    ['-'] * 3,
                    ["+<+y>[+ci]u", "+<+y>[+c]ikek", "+<+y>[+c]iki"],
                    ['-'] * 3,
                ],
                [
                    ["+t'stegennga", "+t'stegenkuk", "+t'stegenkut"],
                    ['-'] * 3,
                    ["+tegnegu", "+t'stegenkek", "+t'stegenki"],
                    ['-'] * 3,
                ],
                [
                    ["+t'sia", "+t'sikuk", "+t'sikut"],
                    ['-'] * 3,
                    ["+t'siu", "+t'sikek", "+t'siki"],
                    ['-'] * 3,
                ],
            ],
            [
                [
                    ['~[+t]anga', '~[+t]akuk', '~[+t]akut'],
                    ['~[+t]aten', '~[+t]atek', '~[+t]aci'],
                    ['~[+t]agu', '~[+t]akek', '~[+t]aki'],
                    ['-'] * 3,
                ],
                [
                    ['~[+t]agnenga', '~[+t]agnekuk', "~[+t]agnekut"],
                    ['~[+t]agten', '~[+t]agtek', "~[+t]agci"],
                    ['~[+t]agnegu', '~[+t]agnekek', '~[+t]agneki'],
                    ['-'] * 3,
                ],
                [
                    ['~[+t]atnga', '~[+t]atkuk', '~[+t]atkut'],
                    ['~[+t]aten', "~[+t]at'ek", "~[+t]at'si"],
                    ['~[+t]atgu', '~[+t]atkek', '~[+t]atki'],
                    ['-'] * 3,
                ],
            ],
            [[['-'] * 3] * 4] * 3,
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
        [
            [
                [
                    ['-'] * 3,
                    ['~ngamken', '~ngamtek', '~ngamci'],
                    ["~ngamgu", "~ngamkek", '~ngamki'],
                    ["~ngamni", "~ngamtek", '~ngamteng'],
                ],
                [
                    ['-'] * 3,
                    ['~ngamken', '~ngamtek', '~ngamci'],
                    ["~ngamt'gen'gu", "~ngamt'gen'kek", "~ngamt'gen'ki"],
                    ["~ngamt'gni", "~ngamt'gtek", "~ngamt'gteng"],
                ],
                [
                    ['-'] * 3,
                    ['~ngamken', '~ngamtek', '~ngamci'],
                    ["~ngamt'gu", "~ngamt'kek", "~ngamt'ki"],
                    ["~ngamt'ni", "~ngamt'stek", "~ngamt'steng"],
                ],
            ],
            [
                [
                    ["~ngaugnga", "~ngaugkuk", "~ngaugkut"],
                    ['-'] * 3,
                    ['~ngagu', '~ngaugkek', "~ngaugki"],
                    ['~ngaugni', '~ngaugtek', "~ngaugteng"],
                ],
                [
                    ["~ngaugt'gennga", "~ngaugt'kuk", "~ngaugt'kut"],
                    ['-'] * 3,
                    ["~ngaugt'gengu", "~ngaugt'genkek", "~ngaugt'genki"],
                    ["~ngaugt'gni", "~ngaugt'gtek", "~ngaugt'gteng"],
                ],
                [
                    ["~ngaugcia", "~ngaugcikuk", "~ngaugcikut"],
                    ['-'] * 3,
                    ["~ngaugciu", "~ngaugcikek", "~ngaugciki"],
                    ["~ngaugt'sni", "~ngaugt'stek", "~ngaugt'steng"],
                ],
            ],
            [
                [
                    ['~nganga', '~ngakuk', '~ngakut'],
                    ['~ngaten', '~ngatek', '~ngaci'],
                    ['~ngagu', "~ngakek", '~ngaki'],
                    ['~ngani', '~ngatek', "~ngateng"],
                ],
                [
                    ['~ngagnenga', '~ngagnekuk', '~ngagnekut'],
                    ['~ngagten', '~ngagtek', "~ngagci"],
                    ['~ngagnegu', "~ngagnekek", '~ngagneki'],
                    ['~ngagni', '~ngagtek', '~ngagteng'],
                ],
                [
                    ['~ngatnga', '~ngatkuk', '~ngatkut'],
                    ['~ngaten', "~ngat'ek", "~ngat'si"],
                    ['~ngatgu', '~ngatkek', '~ngatki'],
                    ['~ngatni', "~ngat'stek", "~ngat'steng"],
                ],
            ],
            [
                [
                    ['~ngamia', '~ngamikuk', '~ngamikut'],
                    ['~ngamiten', '~ngamitek', '~ngamici'],
                    ['~ngamiu', "~ngamikek", '~ngamikegki'],
                    ['-'] * 3,
                ],
                [
                    ["~ngamegt'gennga", "~ngamegt'genkuk", "~ngamegt'genkut"],
                    ["~ngamegt'gten", "~ngamegt'gtek", "~ngamegt'gci"],
                    ["~ngamegt'gengu", "~ngamegt'genkek", "~ngamegt'genki"],
                    ['-'] * 3,
                ],
                [
                    ["~ngamegt'nga", "~ngamegt'kuk", "~ngamegt'kut"],
                    ["~ngamegt'sten", "~ngamegt'stek", "~ngamegt'si"],
                    ["~ngamegt'gu", "~ngamegt'kek", "~ngamegt'ki"],
                    ['-'] * 3,
                ],
            ],
        ],
    ]),
}


def inflection_data(root):
    if root.pos in ENDINGS:
        return inflect(root)
    else:
        return None


def inflect(root):
    '''
    return [build_table(s, column_headers,
            [TableRow(rh, ['-' if c == '-' else morpho_join([entry, c])
                           for c in row])
             for rh, row in zip(row_headers, cells[i])])
            for i, s in enumerate(HIERARCHY[root.pos])]
    '''
    return list(build_tables(root))
