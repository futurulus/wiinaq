from functools import lru_cache
import re
import sys

import pynini as f

u = f.string_map
x = f.cross

POLYGRAPHS = {
    'Ⓖ': 'ng',
    'Ⓗ': 'hng',
    'Ⓛ': 'll',
    'Ⓜ': 'hm',
    'Ⓝ': 'hn',
}  # ⒶⒷⒸⒹⒺⒻⒾⒿⓀⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ

PREFIXES = {
    # Longer prefixes should come first so they don't get shadowed
    '<Y': '+<+y>[+c]',
    '<J': '-<~g>{+e}',
    '<I': '+<+y>[+ci]',
    '<D': '+<+g>[+t]',
    '<S': '+<+s>[+ci]',

    '<H': "+'<+>",
    '<K': '-g{+k}',
    '<N': '+g[~]',

    '<A': '-{+}',
    '<E': '-{+e}',
    '<G': '-<~g>',
    '<T': '~[+t]',
    '<P': '+<~g>',
    '<Z': '+[+t]',
    '<W': '~{~}',
    '<C': '~[+c]',
}

CONSONANTS = 'ptckqwlysgrmnRⒼⒽⓁⓂⓃbdfhjvxz'
VOWELS = 'aeiuo'
SIGMA_REAL = set([chr(i) for i in range(1, 256)])
SIGMA = set(
    [chr(i) for i in range(1, 91)] +
    ['\\[', '\\\\', '\\]'] +
    [chr(i) for i in range(94, 256)] +
    list(POLYGRAPHS)
)
SIGMA_STAR = u(SIGMA).star


def morpho():
    lexicon = {
        '^n': ['qeneq', 'iraluq', 'iluwaq', 'suk'],
        '^i': ['qawar-', 'kuingte-', 'age-', 'alinge-', 'kuimar-', 'mite-', "mingq'rte-"],
        '^t': ["tang'r-", 'atur-', 'niute-'],
        '^w': ['ner-', 'pitur-', 'liite-'],
        '^*': ['ai-', 'pi-'],

        'nn': ['+piaq', '-sinaq'],
        'ni': ['-li-', '-yug-'],
        'nt': ['+illqur-', '+ir-'],
        'nw': ['-ngcar'],
        'n*': ['-ku', '-ipia'],

        'in': ['-lleq'],
        'ii': ['+uaqiinar-'],
        'it': ['+sqe-', '+ute-'],
        'iw': [],
        'i*': ['+uaqitek'],

        'tn': ['-lleq'],
        'ti': ['+i-', '-qsag-'],
        'tt': ["+t'staar-"],
        'tw': [],
        't*': [],

        'vn': ['+suuteq', '+wik'],
        'vv': ['+piar-', "-n'ite-", '-yug-', "-ngnaq'rte-"],
        'vi': ['+yugnga-'],
        'vt': ['+ciaqe-'],
        'vw': [],
        'v*': ['+nguaqina'],

        '*n': ['-rwalleq'],
        '*v': ['+ar-'],
        '*i': ['+guirte-'],
        '*t': ["+gui'a-"],
        '*w': ['+te-'],
        '**': ['+ku-'],

        'n$': ['-k', '-t', '-mi'],
        'i$': ['-uq', '-ua', '-llria', '+kuma'],
        't$': ['-aqa', '-a', '+kii'],
        '*$': [],
    }
    distribution_targets = {
        'vn': ['in', 'tn', 'wn'],
        'vv': ['ii', 'tt', 'ww'],
        'vi': ['ii', 'ti', 'wi'],
        'vw': ['iw', 'tw', 'ww'],
        'v*': ['i*', 't*', 'w*'],
    }
    distributed_lexicon = {}
    for pos, words in lexicon.items():
        targets = distribution_targets.get(pos, [pos])
        for target in targets:
            distributed_lexicon.setdefault(target, []).extend(words)

    matches = [
        'n@ @n',
        'n@ @*',
        'i@ @i',
        'i@ @*',
        't@ @t',
        't@ @*',
        'w@ @i',
        'w@ @t',
        'w@ @w',
        'w@ @*',
        '*@ @n',
        '*@ @i',
        '*@ @t',
        '*@ @w',
        '*@ @*',
    ]
    # framework = '@^' + u(matches).star + '$@'

    # seqs = framework
    # for pos, words in distributed_lexicon.items():
    #     seqs @= rewrite(x(f'@{pos}@', u(set(words))))

    # infer_framework = f.invert(seqs)

    # combine = combination_fst()

    # words = seqs.project('output') @ combine

    # typo_words = words
    # typo_words @= confusion('g', 'r', before_a=u(SIGMA - {'n'}))
    # typo_words @= rewrite(x("'", f.union("'", '')))
    # typo_words @= rewrite(x('e', f.union('e', '')))
    # typo_words @= rewrite(x('R', f.union('R', 'r')))

    # for a, b in [
    #     ('q', 'k'),
    #     ('e', "'"),
    #     ('aa', 'a'),
    #     ('ii', 'i'),
    #     ('uu', 'u'),
    # ]:
    #     typo_words @= confusion(a, b)

    # decoder = f.invert(typo_words)

    # for query in [
    #     "alingyun'ituq",
    #     "kuimallria",
    #     "mit'uq",
    #     "mingq'rtengnaq'rt'kuma",
    #     "kawaartuq",
    #     "pin'itua",
    # ]:
    #     print(query)
    #     for istr, ostr in paths(query @ decoder):
    #         print(f'  {ostr}')
    #     print('')

    # print('---\n')

    for query in [
        "alinge- +<+y>[+c]ug- -n'ite- -uq",
        "kuimar- -llria",
        "mite- -aqa",
        "mingq'rte- -ngnaq'rte- +kuma",
        "qawar- -{+}uq",
        "pi- -n'ite- -ua",
    ]:
        print(query)
        # for istr, ostr in paths(query @ combine):
        #     print(f'  {ostr}')
        chunks = [chunk.rstrip('-') for chunk in query.split()]
        print(f'  {morpho_join(chunks)}')
        print('')


def morpho_join(chunks):
    query = escape("- ".join(chunks))

    combine = combination_fst()
    try:
        _, ostr = next(paths(query @ combine))
    except StopIteration:
        raise StopIteration(query) from None
    return unescape(ostr)


def escape(s):
    r'''
    >>> escape('[中\\文]')
    '\\[\xe4\xb8\xad\\\\\xe6\x96\x87\\]'
    '''
    s = map_character_combinations(s)
    return s.encode('utf-8').decode('latin-1').translate(str.maketrans({
        '\\': r'\\',
        '[': r'\[',
        ']': r'\]',
    }))


def unescape(s):
    r'''
    >>> unescape('\\[\xe4\xb8\xad\\\\\xe6\x96\x87\\]')
    '[中\\文]'
    '''
    return unmap_character_combinations(debackslash(s.encode('latin-1').decode('utf-8')))


def map_character_combinations(s):
    r"""
    >>> map_character_combinations(r'alla- +<+y>[+c]ug')
    'aⓁa- <Yug'
    """
    for short, long in PREFIXES.items():
        s = s.replace(long, short)
    for short, long in POLYGRAPHS.items():
        s = s.replace(long, short)
    return s


def unmap_character_combinations(s):
    r"""
    >>> unmap_character_combinations("aⓁa- <Yug")
    'alla- +<+y>[+c]ug'
    """
    for short, long in POLYGRAPHS.items():
        s = s.replace(short, long)
    for short, long in PREFIXES.items():
        s = s.replace(short, long)
    return s


def paths(fst):
    p = fst.paths()
    while not p.done():
        yield (p.istring(), p.ostring())
        p.next()


def paths_acc(acc):
    p = acc.paths()
    while not p.done():
        yield p.istring()
        p.next()


def rewrite(rule, before='', after=''):
    return f.cdrewrite(rule, before, after, SIGMA_STAR)


@lru_cache(maxsize=1)
def combination_fst():
    fst = apply_negative_fst()

    vowel_alternate = vowel_alternation_fst()
    print("composing", file=sys.stderr)
    fst @= vowel_alternate
    del vowel_alternate
    print("optimizing", file=sys.stderr)
    fst.optimize()

    join = parse_rules(r"""
        # # Drop root-final e on special noun endings before k
        # /[EA]- ~k/k/
        # # Replace root-final e with apostrophe:
        # #   CKeC  where K is voiceless
        # /[eEA]- [-+~]/'/[Ⓒ][ptckqsgrⒽⓁⓂⓃ]/[Ⓒ]/
        # #   KeCC
        # /[eEA]- [-+~]/'/[ptckqsgrⒽⓁⓂⓃ]/[Ⓒ][Ⓒ]|[Ⓒ]'[Ⓥ]/
        # #   VgeV.  (or r instead of g)
        # /[eEA]- [-+~]/'/[Ⓥ][gr]/[Ⓥ][^]/
        # # Keep it when it would otherwise result in CCC
        # /[eA]- [-+~]/e/[Ⓒ][Ⓒ]/[Ⓒ]/
        # /[eA]- [-+~]/e/[Ⓒ]/[Ⓒ][Ⓒ]|[Ⓒ]'[Ⓥ]/
        # # Otherwise drop it
        # /[eA]- [-+~]//

        # Noun stem endings: -a, -eq
        /[AE]- -a/e- -a//[^]/ ?
        /[AE]- -i/e- -i//[^]/ ?
        # piugtA -a => piugtii, niuwasuutE -a => niuwasuutii
        /[AE]- -a/ii/
        # piugtA -i => piugtai, niuwasuutE -i => niuwasuutai
        /[AE]- -i/ai/

        # "Strong" noun stem endings
        # taquka\ra +et => taquka\ra at => taqukaraat
        /a[gr]*- [-+~]e/aa/
        /i[gr]*- [-+~]e/ii/
        /u[gr]*- [-+~]e/uu/
        # nuter -a => nutra
        /rr- -|gg- -//
        # kiweg -a => kiuga
        /weg- -/ug/[Ⓥ][Ⓒ]/[aiu]/
        /wer- -/ur/[Ⓥ][Ⓒ]/[aiu]/
        /eg- -/g/[Ⓥ][Ⓒ]/[aiu]/
        /er- -/r/[Ⓥ][Ⓒ]/[aiu]/

        # Plus-type + endings mostly concatenate
        # ??? what happens to the e here?
        /[rg]*- +e//[aiu]/
        /*- +///[ⓋⒸ']/
        # nere +uq => ner'uq
        /e- +/'/[gr]/[Ⓥ']/
        # qitenge +uq => qitenguq, ike '\um => ik'\um => ik'um
        /e- +///[Ⓥ']/
        /'- +///[Ⓒ]/
        # kiweg +a => kiwg +a => kiuga
        /weg- +/ug/[Ⓥ][Ⓒ]/[Ⓥ]/
        /wer- +/ur/[Ⓥ][Ⓒ]/[Ⓥ]/
        /eg- +/g/[Ⓥ][Ⓒ]/[Ⓥ]/
        # nater +en => natren
        /er- +/r/[Ⓥ][Ⓒ]/[Ⓥ]/
        # tape +gkunani => tap'gkunani
        /e- +/'/[stpkqc]/[gr]/
        # Demonstrative ending: tamaa +\um => tamaatum
        # This is a horrible hack. The good alternative would be to allow having
        # multiple roots, which demonstratives have (tamaatu-, tamaaku-, tamaa-).
        /- +\\/t/aa|ii|uu/

        # Concatenate if there's anything after the +
        /- +///[ⓋⒸ']/
        # Otherwise: empty noun endings
        /te- +/teq/
        /r- +|r*- +/q/
        /g- +|g*- +/k/
        /[eA]- +/a/
        /E- +/eq/

        /- +//

        # Minus-type - endings subtract the previous consonant
        /*- -//
        /g- -//[iue]/[aiu]/
        /er- -/e//[aiu]/
        /[Ⓒ]- -//
        /t'e- -/t'- -/
        /pe- -p/pe/
        /te- -t/te/
        /ce- -c/ce/
        /ke- -k/ke/
        /qe- -q/qe/
        /se- -s/se/
        /ge- -g/ge/
        /re- -r/re/
        /Ⓗe- -Ⓗ/Ⓗe/
        /Ⓛe- -Ⓛ/Ⓛe/
        /Ⓜe- -Ⓜ/Ⓜe/
        /Ⓝe- -Ⓝ/Ⓝe/
        /e- -/'/[ptckqsgrⒼⒽⓁⓂⓃ]/[ptckqsgrⒽⓁⓂⓃ][Ⓒ]/
        # qutA -mnek => qute -mnek => qutemnek
        /e- -/e/[Ⓒ]/[Ⓒ][Ⓒ]/
        # piugtA -gun => piugte -gun => piugt'gun
        /e- -/'/[Ⓒ][ptckqsgrⒼⒽⓁⓂⓃ]/[ptckqsgrⒼⒽⓁⓂⓃ]/
        # piugtA -mi => piugte -mi => piugtemi
        /e- -/e/[Ⓒ][Ⓒ]/[Ⓒ]/
        /e- -/'//[Ⓥ]/
        /e- -//

        /- -//
        *

        # # Assimilating ~ endings are mostly like plus-type, but sometimes combine
        # # Special noun endings
        # # qute ~ka => qutka
        # /t[AE]- ~k/tk/[Ⓥ]/
        # # piugtA ~ka => piugteka [=> piugt'ka]
        # /t[AE]- ~k/tk/
        # /[AE]- ~/e- ~/

        # /t'e- ~k/Ⓛk/
        # /te- ~k/sk//[Ⓥ]/
        # /te- ~k/'sk///
        # /e- ~k/'gk/[kq]/
        # # nuteg ~ka => nutegka
        # /gg- ~k|g*- ~k|g- ~k/gk//[Ⓥ]/
        # /gg- ~k|g*- ~k|g- ~k/k/
        # # nater ~ka => natqa
        # /er- ~k/q/[Ⓥ][Ⓒ]/[Ⓥ]/
        # # kayar ~ka => kayaqa, minar ~kii => minaqii
        # /rr- ~k|r*- ~k|r- ~k/q/
        # /- ~k/k/[aioul]/
        # /[ⒸⓋ]- ~k/k/
        # # missing apostrophe additions for triple consonants here?

        # # kiweg ~ganun => kiw ~ganun => kiuganun
        # /wer- ~g/ur/[Ⓥ]/[Ⓥ]/
        # /weg- ~g/ug/[Ⓥ]/[Ⓥ]/
        # # nater ~ga => natra
        # /er- ~g/r/[Ⓥ][Ⓒ]/[Ⓥ]/
        # /eg- ~g/g/[Ⓥ][Ⓒ]/[Ⓥ]/
        # /e- ~g/'g//[Ⓒ]/
        # /gg- ~g|g*- ~g/g/
        # /rr- ~g|r*- ~g|r- ~g/r/
        # /[Ⓒ]- ~g/g/

        # # et'e ~luni => ell'uni
        # /t'e- ~l/Ⓛ'/
        # # et'e ~ngama => ellngama
        # /t'e- ~/Ⓛ//Ⓖ/
        # # mikte ~lnguq => mik'llnguq
        # /te- ~l/'Ⓛ/[Ⓒ]/[Ⓒ]/
        # # pekte ~luni => peklluni
        # /te- ~l/Ⓛ/
        # # aiwite ~ngama => aiwicama
        # /te- ~Ⓖ/'c/[Ⓒ]/[Ⓒ]/
        # /te- ~Ⓖ/c/
        # # ule ~luni => ul'uni
        # /le- ~l/l'/
        # /e- ~l/'Ⓛ/[Ⓒ][ptckqsgrⒽⓁⓂⓃ]/
        # /e- ~Ⓖ/'Ⓖ/[Ⓒ][ptckqsgrⒽⓁⓂⓃ]/
        # # cupugg ~luni => cupuglluni
        # /gg- ~l/gⓁ/
        # # angq'rr ~luni => angq'rlluni
        # /rr- ~l/rⓁ/
        # # caqe ~luni => caqlluni
        # /e- ~l/Ⓛ/[qk]/
        # # age ~luni => agluni
        # /e- ~//

        # /a- ~a/a'a/
        # /i- ~i/i'i/
        # /u- ~u/u'u/
        # /e- ~///[aiu]/
        # /i- ~/iy//[au]/
        # /u- ~/uw//[ai]/

        # # kate ~na => kan'a
        # /te- ~n/n'/
        # # ike ~na => ikna
        # /e- ~///n/

        /- ~//

        # Break up triple vowels
        /uu/u'u/[Ⓥ]|[Ⓥ]\\/
        # ki\ir -it => kii'it
        /ii/i'i/[Ⓥ]|[Ⓥ]\\/
        # ki\ir -a => kiiya
        /i/iy/[Ⓥ]|[Ⓥ]\\/[Ⓥ]/
        # qaur -a => qauwa
        /u/uw/[Ⓥ]|[Ⓥ]\\/[Ⓥ]/
        /a/a'/[Ⓥ]|[Ⓥ]\\/[Ⓥ]/
        *

        # Get rid of some remaining technical notation
        /rr/r/
        /gg/g/
        # Backslash-vowel disappears in a closed syllable
        # has to be same vowel?
        /\\//[aiu]/[aiu][Ⓒ][Ⓥ]/
        /\\[aiu]//[aiu]/[Ⓒ]/
        # Backslash-g/r disappears before a consonant
        # /X\\X/X/  --which X do we need this for?
        /\\///[gr][aiu][Ⓥ]/
        /a\\[gr]a/a'a//[Ⓒ]/
        /i\\[gr]i/i'i//[Ⓒ]/
        /u\\[gr]u/u'u//[Ⓒ]/
        /i\\[gr]/iy//[au][Ⓒ]/
        /u\\[gr]/uw//[ai][Ⓒ]/
        /\\//
        *
    """)
    print("composing", file=sys.stderr)
    fst @= join
    del join
    print("optimizing", file=sys.stderr)
    fst.optimize()

    return fst


@lru_cache(maxsize=1)
def apply_negative_fst():
    return parse_rules(r"""
        # Cancel out double negations
        /N- !/- /
        /[au\\]iT- !/r- /
        /kiT- !/tu- /
        /iX- !/ngq'rr- /
        # /T- !/- !/[Ⓥ]/
        # /T- !/e- !/[Ⓒ]/

        # / / !/[NTX]-/[-+~<]/

        # Negatives of -tu- roots
        /tu- !/kiT- !/
        /tuN- !/kiT- !/
        /ki- !+n/kin/
        /ki- !~lngu/kilngu/
        /ki- !~l/kin'll/

        # Negative endings
        /!~luten/+nak/
        /!~lua/+nii/
        /!~lu/+na/
        /!~lngu/-nilngu/
        /!~l/-n'll/
        /!-ll[r']ianga/~lngua(nga)/
        /!-ll[r']i[ai]/~lngu//[tkc]/
        /!-ll[r']ia/~lnguq/
        /!~ng/~lng/
        /![-+~]/~ll//k/
        /!/-n'ite- /

        # Negative -te- roots
        /iT- ~l/i- ~l/
        /ggT- /gte- /
        /rrT- /rte- /
        /T- +n/n/
        /T- /te- /

        # Add -(g)ku before +na endings (e.g. -gkunani)
        / +n/ <Nkun/
        *
    """)


@lru_cache(maxsize=1)
def vowel_alternation_fst():
    return parse_rules(r"""
        # '<Y': '+<+y>[+c]',
        /<Y/+y/[aiou]- /
        /<Y/+c/[grⓁ]- /
        /<Y/+/
        # '<J': '-<~g>{+e}',
        /<J/~g/[Ⓥ]- /
        /<J/+e/*- |[iue]g- |er- /
        /<J/-/
        # '<I': '+<+y>[+ci]',
        /<I/+y/[aiou]- /
        /<I/+ci/[grⓁ]- /
        /<I/+/
        # '<D': '+<+g>[+t]',
        /<D/+g/[aiou]- /
        /<D/+t/[grⓁ]- /
        /<D/+/
        # '<S': '+<+s>[+ci]',
        /<S/+s/[aiou]- /
        /<S/+ci/[grⓁ]- /
        /<S/+/

        # '<H': "+'<+>",
        /<H/+/[aiou]- /
        /<H/+'/
        # '<K': '-g{+k}',
        /<K/+k/*- |[iue]g- |er- /
        /<K/-g/
        # '<N': '+g[~]',
        /<N/~/[grⓁ]- /
        /<N/+g/

        # '<A': '-{+}',
        /<A/+/*- |[iue]g- |er- /
        /<A/-/
        # '<E': '-{+e}',
        /<E/+e/*- |[iue]g- |er- /
        /<E/-/
        # '<G': '-<~g>',
        #   special rule: -<...> is valid after [eA]
        /<G/~g/[ⓋA]- /
        /<G/-/
        # '<T': '~[+t]',
        /<T/+t/[grⓁ]- /
        /<T/~/
        # '<P': '+<~g>',
        /<P/~g/[aiou]- /
        /<P/+/
        # '<Z': '+[+t]',
        /<Z/+t/[grⓁ]- /
        /<Z/+/
        # '<W': '~{~}',
        /<W/~/
        # '<C': '~[+c]',
        /<C/+c/[grⓁ]- /
        /<C/~/
        *
    """)


def confusion(a, b, before_a='', after_a='', before_b='', after_b=''):
    return (
        rewrite(x(a, f.union(a, '>')), before_a, after_a)
        @ rewrite(x(b, f.union(b, a)), before_b, after_b)
        @ rewrite(x('>', b), before_a, after_a)
    )


def parse_rules(rules):
    lines = rules.splitlines()
    fst = None

    for line in lines:
        if fst and line.strip() == "*":
            print("optimizing", file=sys.stderr)
            fst.optimize()
            continue
        if '/' not in line or line.strip().startswith('#'):
            continue
        print(line, file=sys.stderr)
        cols = line.split('/')[1:-1]
        src, tgt = cols[:2]
        before = after = ''
        if len(cols) >= 3:
            before = parse_acc(cols[2])
        if len(cols) >= 4:
            after = parse_acc(cols[3])

        rule_fst = rewrite(
            x(parse_acc(src), parse_acc(tgt)),
            before,
            after,
        )
        if fst is None:
            fst = rule_fst
        else:
            fst @= rule_fst

    return fst


def parse_acc(expr):
    r'''
    Builds an FST from an expression in a dramatically simplified subset of
    regex syntax.

    An expression can be a disjunction of strings separated by vertical bar
    characters |, where each of the strings can contain character sets enclosed
    in [square brackets]. A character set that starts with a caret ^ is negated.
    Square brackets and vertical bars can be escaped with backslashes, and
    backslashes can themselves be escaped by doubling them.  There are no
    parentheses (so disjunctions cannot be nested or partial).

    >>> sorted(paths_acc(parse_acc('ab|[cd]')))
    ['ab', 'c', 'd']
    >>> sorted(paths_acc(parse_acc('a\\|b|[c\\|d]')))
    ['a|b', 'c', 'd', '|']
    >>> not_cd = parse_acc('[^cd]'); sorted(SIGMA_REAL - set(paths_acc(not_cd)))
    ['c', 'd']
    '''
    terms = [
        term[:-1]
        for term in re.split(r'''
            (
                (?:[^|\\]|\\.)*  # Zero or more non-bars and escaped characters
                \|               # followed by a bar (is the counterintuitive
            )                    # "delimiter" we're splitting on)
        ''', expr + '|', flags=re.VERBOSE)
        if term  # re.split returns empty strings between these "delimiters"
    ]

    term_accs = []
    for term in terms:
        seq_acc = ''
        while True:
            match = re.match(r'''
                (
                    (?:[^[\\]|\\.)*      # Zero or more non-brackets and escaped characters
                )
                \[
                    (
                        (?:[^]\\]|\\.)+  # followed by a bracketed group of non-brackets and
                    )                    # escaped characters (non-empty)
                \]
            ''', term, flags=re.VERBOSE)
            if match is None:
                seq_acc += escape(debackslash(term))
                break
            seq_acc += escape(debackslash(match.group(1)))
            chars = match.group(2)
            chars = chars.replace('Ⓒ', CONSONANTS).replace('Ⓥ', VOWELS)
            seq_acc += f.union(*(
                SIGMA - charset(chars[1:])
                if chars[0] == '^'
                else charset(chars)
            ))
            term = term[match.end():]
        term_accs.append(seq_acc)
    return f.union(*term_accs)


def debackslash(s):
    r'''
    >>> debackslash(r'a\\\[a')
    'a\\[a'
    '''
    return re.sub(r'\\(.)', r'\1', s)


def charset(chars):
    chars = debackslash(chars)
    accepted = set(chars)
    if '[' in accepted:
        accepted = (accepted | {'\\['}) - {'['}
    if ']' in accepted:
        accepted = (accepted | {'\\]'}) - {']'}
    if '\\' in accepted:
        accepted = (accepted | {'\\\\'}) - {'\\'}
    return accepted


if __name__ == '__main__':
    morpho()
