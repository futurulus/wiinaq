import gzip
import re
import sys
from functools import lru_cache
from pathlib import Path

import pynini as f

u = f.string_map
x = f.cross

# Various single-symbol substitutions of multi-character strings
HIGH_BYTE = 'HB'
SPACE = 'SPACE'
POLYGRAPHS = [
    # Longer polygraphs should come first so they don't get shadowed
    'hng',
    'ng',
    'll',
    'hm',
    'hn',
]
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

CONSONANTS = list('ptckqwlysgrmnRbdfhjvxz') + POLYGRAPHS
VOWELS = list('aeiuo')
SIGMA_REAL = set([chr(i) for i in range(1, 128)])
SIGMA = (
    [chr(i) for i in range(1, 91)] +
    [chr(i) for i in range(94, 128)] +
    [r'\[', r'\\', r'\]', HIGH_BYTE] +
    [f'[{p}]' for p in POLYGRAPHS + list(PREFIXES)]
)
SIGMA_STAR = u(SIGMA).star
SIGMA_STAR.optimize()

COMBINATION_RULES = r"""
    # == Negation rules ==

    # Cancel out double negations
    /N !/ /
    /{au\\}iT !/r /
    /kiT !/tu /
    /iX !/[ng]q'rr /
    # /T !/ !/{Ⓥ}/
    # /T !/e !/{Ⓒ}/

    # / / !/{NTX}/{-+~<}/

    # Negatives of -tu- roots
    /tu !/kiT !/
    /tuN !/kiT !/
    /ki !+n/kin/
    /ki !~l[ng]u/kil[ng]u/
    /ki !~l/kin'[ll]/

    # Negative endings
    /!~luten/+nak/
    /!~lua/+nii/
    /!~lu/+na/
    /!~l[ng]u/-nil[ng]u/
    /!~l/-n'[ll]/
    /!-ll{r'}ia[ng]a/~l[ng]ua([ng]a)/
    /!-ll{r'}i{ai}/~l[ng]u//{tkc}/
    /!-ll{r'}ia/~l[ng]uq/
    /!~[ng]/~l[ng]/
    /!{-+~}/~[ll]//k/
    /!/-n'ite /

    # Negative -te- roots
    /iT ~l/i ~l/
    /ggT /gte /
    /rrT /rte /
    /T +n/n/
    /T /te /

    # Add -(g)ku before +na endings (e.g. -gkunani)
    / +n/ [<N]kun/
    *

    # == Vowel alternation ==

    # '<Y': '+<+y>[+c]',
    /[<Y]/+y/{aiou} /
    /[<Y]/+c/{gr[ll]} /
    /[<Y]/+/
    # '<J': '-<~g>{+e}',
    /[<J]/~g/{Ⓥ} /
    /[<J]/+e/* |{iue}g |er /
    /[<J]/-/
    # '<I': '+<+y>[+ci]',
    /[<I]/+y/{aiou} /
    /[<I]/+ci/{gr[ll]} /
    /[<I]/+/
    # '<D': '+<+g>[+t]',
    /[<D]/+g/{aiou} /
    /[<D]/+t/{gr[ll]} /
    /[<D]/+/
    # '<S': '+<+s>[+ci]',
    /[<S]/+s/{aiou} /
    /[<S]/+ci/{gr[ll]} /
    /[<S]/+/

    # '<H': "+'<+>",
    /[<H]/+/{aiou} /
    /[<H]/+'/
    # '<K': '-g{+k}',
    /[<K]/+k/* |{iue}g |er /
    /[<K]/-g/
    # '<N': '+g[~]',
    /[<N]/~/{gr[ll]} /
    /[<N]/+g/

    # '<A': '-{+}',
    /[<A]/+/* |{iue}g |er /
    /[<A]/-/
    # '<E': '-{+e}',
    /[<E]/+e/* |{iue}g |er /
    /[<E]/-/
    # '<G': '-<~g>',
    #   special rule: -<...> is valid after {eA}
    /[<G]/~g/{ⓋA} /
    /[<G]/-/
    # '<T': '~[+t]',
    /[<T]/+t/{gr[ll]} /
    /[<T]/~/
    # '<P': '+<~g>',
    /[<P]/~g/{aiou} /
    /[<P]/+/
    # '<Z': '+[+t]',
    /[<Z]/+t/{gr[ll]} /
    /[<Z]/+/
    # '<W': '~{~}',
    /[<W]/~/
    # '<C': '~[+c]',
    /[<C]/+c/{gr[ll]} /
    /[<C]/~/
    *

    # == Combination ==

    # Noun stem endings: -a, -eq
    /{AE} -a/e -a//{ⓋⒸ'}/ ?
    /{AE} -i/e -i//{ⓋⒸ'}/ ?
    # piugtA -a => piugtii, niuwasuutE -a => niuwasuutii
    /{AE} -a/ii/
    # piugtA -i => piugtai, niuwasuutE -i => niuwasuutai
    /{AE} -i/ai/

    # "Strong" noun stem endings
    # taquka\ra +et => taquka\ra at => taqukaraat
    /a{gr}* {-+~}e/aa/
    /i{gr}* {-+~}e/ii/
    /u{gr}* {-+~}e/uu/
    # nuter -a => nutra
    /rr -|gg -//
    # kiweg -a => kiuga
    /weg -/ug/{Ⓥ}/{aiu}/
    /wer -/ur/{Ⓥ}/{aiu}/
    /eg -/g/{Ⓥ}{Ⓒ}/{aiu}/
    /er -/r/{Ⓥ}{Ⓒ}/{aiu}/
    *

    # Plus-type + endings mostly concatenate
    # ??? what happens to the e here?
    /{rg}* +e//{aiu}/
    /* +///{ⓋⒸ'}/
    # nere +uq => ner'uq
    /e +/'/{gr}/{Ⓥ'}/
    # qitenge +uq => qitenguq, ike '\um => ik'\um => ik'um
    /e +///{Ⓥ'}/
    /' +///{Ⓒ}/
    # kiweg +a => kiwg +a => kiuga
    /weg +/ug/{Ⓥ}/{Ⓥ}/
    /wer +/ur/{Ⓥ}/{Ⓥ}/
    /eg +/g/{Ⓥ}{Ⓒ}/{Ⓥ}/
    # nater +en => natren
    /er +/r/{Ⓥ}{Ⓒ}/{Ⓥ}/
    # tape +gkunani => tap'gkunani
    /e +/'/{stpkqc}/{gr}/
    # Demonstrative ending: tamaa +\um => tamaatum
    # This is a horrible hack. The good alternative would be to allow having
    # multiple roots, which demonstratives have (tamaatu-, tamaaku-, tamaa-).
    / +\\/t/aa|ii|uu/

    # Empty noun endings
    /te +/teq//[EOS]/
    /r +|r* +/q//[EOS]/
    /g +|g* +/k//[EOS]/
    /A +/a//[EOS]/
    /{eE} +/eq//[EOS]/
    # Concatenate if there's anything after the +
    # / +///{ⓋⒸ'}/

    / +//
    *

    # Minus-type - endings subtract the previous consonant
    /* -//
    /g -//{iue}/{aiu}/
    /er -/r//{aiu}/
    /r -//
    # /{Ⓒ} -//
    /t'e -/t' -/
    /pe -p/pep/
    /te -t/tet/
    /ce -c/cec/
    /ke -k/kek/
    /qe -q/qeq/
    /se -s/ses/
    /ge -g/geg/
    /re -r/rer/
    /[hng]e -[hng]/[hng]e/
    /[ll]e -[ll]/[ll]e/
    /[hm]e -[hm]/[hm]e/
    /[hn]e -[hn]/[hn]e/
    /e -/'/{ptckqsgr[ng][ll][hm][hn][hng]}/{ptckqsgr[ll][hm][hn][hng]}{Ⓒ}/
    # qutA -mnek => qute -mnek => qutemnek
    /e -/e/{Ⓒ}/{Ⓒ}{Ⓒ}/
    # piugtA -gun => piugte -gun => piugt'gun
    /e -/'/{Ⓒ}{ptckqsgr[ng][ll][hm][hn][hng]}/{ptckqsgr[ll][hm][hn][hng]}/
    # piugtA -mi => piugte -mi => piugtemi
    /e -/e/{Ⓒ}{Ⓒ}/{Ⓒ}/
    /e -/'//{Ⓥ}/
    /e -//

    / -//{Ⓥ}/
    *

    # Assimilating ~ endings are mostly like plus-type, but sometimes combine
    # Special noun endings
    # qute ~ka => qutka
    /t{AE} ~k/tk/{Ⓥ}/
    # piugtA ~ka => piugteka [=> piugt'ka]
    /t{AE} ~k/t'k/{Ⓒ}/
    /{AE} ~/e ~/

    /t'e ~k/[ll]k/
    /te ~k/sk//{Ⓥ}/
    /te ~k/'sk///
    /e ~k/'gk/{kq}/
    # nuteg ~ka => nutegka
    /gg ~k|g* ~k|g ~k/gk//{Ⓥ}/
    /gg ~k|g* ~k|g ~k/k/
    # nater ~ka => natqa
    /er ~k/q/{Ⓥ}{Ⓒ}/{Ⓥ}/
    # kayar ~ka => kayaqa, minar ~kii => minaqii
    /rr ~k|r* ~k|r ~k/q/
    / ~k/k/{aioul}/
    # /{ⒸⓋ} ~k/k/
    # missing apostrophe additions for triple consonants here?

    # kiweg ~ganun => kiw ~ganun => kiuganun
    /wer ~g/ur/{Ⓥ}/{Ⓥ}/
    /weg ~g/ug/{Ⓥ}/{Ⓥ}/
    # nater ~ga => natra
    /er ~g/r/{Ⓥ}{Ⓒ}/{Ⓥ}/
    /eg ~g/g/{Ⓥ}{Ⓒ}/{Ⓥ}/
    /e ~g/'g//{Ⓒ}/
    /gg ~g|g* ~g/g/
    /rr ~g|r* ~g|r ~g/r/
    # /{Ⓒ} ~g/g/

    # et'e ~luni => ell'uni
    /t'e ~l/[ll]'/
    # et'e ~ngama => ellngama
    /t'e ~/[ll]//[ng]/
    # mikte ~lnguq => mik'llnguq
    /te ~l/'[ll]/{Ⓒ}/{Ⓒ}/
    # pekte ~luni => peklluni
    /te ~l/[ll]/{Ⓥ'}/
    /te ~l/[ll]//{Ⓥ}/
    # aiwite ~ngama => aiwicama
    /te ~[ng]/'c/{Ⓒ}/{Ⓒ}/
    /te ~[ng]/c/{Ⓥ'}/
    /te ~[ng]/c//{Ⓥ}/
    # ule ~luni => ul'uni
    /le ~l/l'/
    /e ~l/'[ll]/{Ⓒ}{pckqsgr[ll][hm][hn][hng]}/
    /e ~[ng]/'[ng]/{Ⓒ}{pckqsgr[ll][hm][hn][hng]}/
    # cupugg ~luni => cupuglluni
    /gg ~l/g[ll]/
    # angq'rr ~luni => angq'rlluni
    /rr ~l/r[ll]/
    # caqe ~luni => caqlluni
    /e ~l/[ll]/{qk}/
    # age ~luni => agluni
    /e ~//

    /a ~a/a'a/
    /i ~i/i'i/
    /u ~u/u'u/
    /e ~///{aiu}/
    /i ~/iy//{au}/
    /u ~/uw//{ai}/

    # kate ~na => kan'a
    /te ~n/n'/
    # ike ~na => ikna
    /e ~///n/

    / ~//
    *

    # Break up triple vowels
    /uu/u'u/{Ⓥ}|{Ⓥ}\\/
    # ki\ir -it => kii'it
    /ii/i'i/{Ⓥ}|{Ⓥ}\\/
    # ki\ir -a => kiiya
    /i/iy/{Ⓥ}|{Ⓥ}\\/{Ⓥ}/
    # qaur -a => qauwa
    /u/uw/{Ⓥ}|{Ⓥ}\\/{Ⓥ}/
    /a/a'/{Ⓥ}|{Ⓥ}\\/{Ⓥ}/

    # Get rid of some remaining technical notation
    /rr/r/
    /gg/g/
    # Backslash-vowel disappears in a closed syllable
    # has to be same vowel?
    # /\\//{aiu}/{aiu}{Ⓒ}{Ⓥ}/
    /\\{aiu}//{aiu}/{Ⓒ}{Ⓒ}|{Ⓒ}[EOS]/
    # *
    # Backslash-g/r disappears before a consonant
    # /X\\X/X/  --which X do we need this for?
    # /\\///{gr}{aiu}{Ⓥ}/
    # /\\{gr}/'/a/a{Ⓒ}/
    # /\\{gr}/'/i/i{Ⓒ}/
    # /\\{gr}/'/u/u{Ⓒ}/
    # /\\{gr}/y/i/{au}{Ⓒ}/
    # /\\{gr}/w/u/{ai}{Ⓒ}/
    /\\//
    *
"""


def morpho():
    lexicon = {
        '^n': ['qeneq', 'iraluq', 'iluwaq', 'suk'],
        '^i': ['qawar', 'kuingte', 'age', 'alinge', 'kuimar', 'mite', "mingq'rte"],
        '^t': ["tang'r", 'atur', 'niute'],
        '^w': ['ner', 'pitur', 'liite'],
        '^*': ['ai', 'pi'],

        'nn': ['+piaq', '-sinaq'],
        'ni': ['-li', '-yug'],
        'nt': ['+illqur', '+ir'],
        'nw': ['-ngcar'],
        'n*': ['-ku', '-ipia'],

        'in': ['-lleq'],
        'ii': ['+uaqiinar'],
        'it': ['+sqe', '+ute'],
        'iw': [],
        'i*': ['+uaqitek'],

        'tn': ['-lleq'],
        'ti': ['+i', '-qsag'],
        'tt': ["+t'staar"],
        'tw': [],
        't*': [],

        'vn': ['+suuteq', '+wik'],
        'vv': ['+piar', "-n'ite", '-yug', "-ngnaq'rte"],
        'vi': ['+yugnga'],
        'vt': ['+ciaqe'],
        'vw': [],
        'v*': ['+nguaqina'],

        '*n': ['-rwalleq'],
        '*v': ['+ar'],
        '*i': ['+guirte'],
        '*t': ["+gui'a"],
        '*w': ['+te'],
        '**': ['+ku'],

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

    # # infer_framework = f.invert(seqs)

    combine = combination_fst()

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
        ['alinge', '+<+y>[+c]ug', "-n'ite", '-uq'],
        ['kuimar', '-llria'],
        ['mite', '-aqa'],
        ["mingq'rte", "-ngnaq'rte", '+kuma'],
        ['qawar', '-{+}uq'],
        ['pi', "-n'ite", '-ua'],
    ]:
        print(query)
        print(f'  {morpho_join(query)}')
        print('')


def morpho_join(chunks):
    query = " ".join([escape(chunk) for chunk in chunks])

    combine = combination_fst()
    try:
        _, ostr = next(paths(f.accep(query) @ combine))
    except StopIteration:
        raise StopIteration(query) from None
    return unescape(ostr)


def escape(s):
    r'''
    >>> escape('[中 \xa0\\文ng]')
    '\\[[HB]d[HB]8[HB]-[SPACE][HB]B[HB][SPACE]\\\\[HB]f[HB]\x16[HB]\x07[ng]\\]'
    '''
    s = s.encode('utf-8').decode('latin-1')
    s = f.escape(s)
    s = map_character_combinations(s)
    return s


def unescape(s):
    r'''
    >>> unescape('\\[[HB]d[HB]8[HB]-[SPACE][HB]B[HB][SPACE]\\\\\xe6\x96\x87[ng]\\]')
    '[中 \xa0\\文ng]'
    '''
    s = unmap_character_combinations(s)
    s = debackslash(s)
    s = s.encode('latin-1').decode('utf-8')
    return s


def map_character_combinations(s):
    r"""
    >>> map_character_combinations('äÂ\xa0allahng +<+y>\\[+c\\]ug')
    '[HB]d[HB]B[HB][SPACE]a[ll]a[hng][SPACE][<Y]ug'
    """
    s = translate_multi(s, {f.escape(long): f'[{short}]' for short, long in PREFIXES.items()})
    s = translate_multi(s, {f.escape(polygraph): f'[{polygraph}]' for polygraph in POLYGRAPHS})
    s = re.sub(r'[\x80-\xff]', lambda match: f'[{HIGH_BYTE}]' + chr(ord(match[0]) - 0x80), s)
    s = s.replace(' ', f'[{SPACE}]')
    return s


def unmap_character_combinations(s):
    r"""
    >>> unmap_character_combinations('[HB]d[HB]B[HB][SPACE]a[ll]a[hng] [<Y]ug')
    'äÂ\xa0allahng +<+y>\\[+c\\]ug'
    """
    s = s.replace(f'[{SPACE}]', ' ')
    s = re.sub(fr'\[{HIGH_BYTE}\].', lambda match: chr(ord(match[0][-1]) + 0x80), s)
    s = translate_multi(s, {f'[{polygraph}]': f.escape(polygraph) for polygraph in POLYGRAPHS})
    s = translate_multi(s, {f'[{short}]': f.escape(long) for short, long in PREFIXES.items()})
    return s


def translate_multi(s, replacements):
    to_replace = "|".join(re.escape(key) for key, _ in replacements.items())
    return re.sub(to_replace, (lambda match: replacements[match[0]]), s)


def paths(fst, symbols=True):
    if symbols:
        ist, ost = fst.input_symbols(), fst.output_symbols()
        p = fst.paths(input_token_type=ist, output_token_type=ost)
    else:
        p = fst.paths()
    while not p.done():
        if symbols:
            yield (symbols_to_string(p.istring()), symbols_to_string(p.ostring()))
        else:
            yield (p.istring(), p.ostring())
        p.next()


def paths_acc(acc, symbols=True):
    for _, ostr in paths(acc, symbols=symbols):
        yield ostr


def global_symbol_table():
    st = f.generated_symbols().copy()
    for i in range(0, 256):
        st.add_symbol(chr(i), key=i)
    return st


def symbols_to_string(sym_str):
    r"""
    >>> symbols_to_string(r'  a   ng a ll [ \ r u  ')
    ' a [ng]a[ll]\\[\\\\ru '
    """
    symbols = [piece for piece in re.split('( )', sym_str) if piece != ''][::2]
    return ''.join(
        f'[{sym}]' if len(sym) > 1 else
        fr'\{sym}' if sym in ('\\', '[', ']') else
        sym
        for sym in symbols
    )


def rewrite(rule, before='', after=''):
    return f.cdrewrite(rule, before, after, SIGMA_STAR)


@lru_cache(maxsize=1)
def combination_fst():
    filename = str(Path(__file__).parent / 'combine.fst.gz')
    try:
        with gzip.open(filename, 'rb') as infile:
            return f.Fst.read_from_string(infile.read())
    except IOError:
        pass

    combine = parse_rules(COMBINATION_RULES)
    st = global_symbol_table()
    combine.set_input_symbols(st)
    combine.set_output_symbols(st)
    with gzip.open(filename, 'wb') as outfile:
        outfile.write(combine.write_to_string())
    return combine


def confusion(a, b, before_a='', after_a='', before_b='', after_b=''):
    return (
        rewrite(x(a, f.union(a, '>')), before_a, after_a)
        @ rewrite(x(b, f.union(b, a)), before_b, after_b)
        @ rewrite(x('>', b), before_a, after_a)
    )


def parse_rules(rules):
    lines = rules.splitlines()
    fst = None
    old_states = 1
    old_arcs = 1

    def log_sizes():
        nonlocal old_states, old_arcs
        states = fst.num_states()
        arcs = num_arcs(fst)
        delta_states = states * 1. / old_states - 1.
        delta_arcs = arcs * 1. / old_arcs - 1.
        old_states = states
        old_arcs = arcs
        print(f"  {states} ({delta_states:.2f}) {arcs} ({delta_arcs:.2f})", file=sys.stderr)

    for line in lines:
        if fst and line.strip() == "*":
            print("optimizing", file=sys.stderr)
            fst.optimize()
            log_sizes()
            continue
        if '/' not in line or line.strip().startswith('#'):
            continue
        print(line, file=sys.stderr)
        rule_fst = parse_rule(line)
        if fst is None:
            fst = rule_fst
        else:
            fst @= rule_fst

        log_sizes()

    return fst


def parse_rule(rule):
    cols = rule.split('/')[1:-1]
    src, tgt = cols[:2]
    before = after = ''
    if len(cols) >= 3:
        before = parse_acc(cols[2])
    if len(cols) >= 4:
        after = parse_acc(cols[3])

    cross = x(parse_acc(src), parse_acc(tgt))
    return rewrite(cross, before, after)


def parse_acc(expr):
    r'''
    Builds an acceptor FST from an expression in a dramatically simplified
    subset of regex syntax.

    An expression can be a disjunction of strings separated by vertical bar
    characters |, where each of the strings can contain character sets enclosed
    in {braces}. A character set that starts with a caret ^ is negated. Braces
    and vertical bars can be escaped with backslashes, and backslashes can
    themselves be escaped by doubling them.  There are no parentheses (so
    disjunctions cannot be nested or partial).

    >>> sorted(paths_acc(parse_acc('ab|{cd}'), symbols=False))
    ['ab', 'c', 'd']
    >>> sorted(paths_acc(parse_acc('a\\|\\{b|{c\\|d}'), symbols=False))
    ['a|{b', 'c', 'd', '|']
    >>> not_cd = parse_acc('{^cd}'); sorted(SIGMA_REAL - set(paths_acc(not_cd, symbols=False)))
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
                    (?:[^{\\]|\\.)*      # Zero or more non-brackets and escaped characters
                )
                \{
                    (
                        (?:[^}\\]|\\.)+  # followed by a bracketed group of non-brackets and
                    )                    # escaped characters (non-empty)
                \}
            ''', term, flags=re.VERBOSE)
            if match is None:
                seq_acc += debackslash(term)
                break
            seq_acc += debackslash(match.group(1))
            chars = match.group(2)
            chars = chars.replace('Ⓒ', ''.join(CONSONANTS)).replace('Ⓥ', ''.join(VOWELS))
            seq_acc += f.union(*(
                set(SIGMA) - charset(chars[1:])
                if chars[0] == '^'
                else charset(chars)
            ))
            term = term[match.end():]
        term_accs.append(seq_acc)
    return f.union(*term_accs)


def debackslash(s):
    r'''
    >>> debackslash(r'a\\\{a')
    'a\\{a'
    '''
    return re.sub(r'\\(.)', r'\1', s)


def charset(chars):
    chunks = re.split(r'(\\.|\[[^\]]*\])', chars)
    accepted = set()
    for chunk in chunks:
        if chunk.startswith('\\'):
            assert len(chunk) == 2
            if chunk[1] in ('[', ']', '\\'):
                accepted.add(chunk)
            else:
                accepted.add(chunk[1])
        elif chunk.startswith('['):
            accepted.add(chunk)
        else:
            accepted.update(chunk)
    return accepted


def num_arcs(fst):
    return sum(fst.num_arcs(state) for state in fst.states())


if __name__ == '__main__':
    morpho()
