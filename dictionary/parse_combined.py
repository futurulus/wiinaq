# -*- coding: utf-8 -*-
r'''
Run as python -m dictionary.parse_combined <combined_dict_file.mdf>

check:
    \codes with spaces before tab
    \sse's that should be \see's (look for "under"?)
    ways of excluding sensitive info (look for \nq "flag"?)
    appropriate handling of him/her
    long strings of repeated characters ('zzz', 'wwwwwww', '------' etc.)

http://downloads.sil.org/legacy/shoebox/MDF_2000.pdf

  54690 \dl    var Dialect
  50548 \so    src Source [name of native speaker]
  21310 \nqq   not Questions and comments: from Joe Kwaraceius < \nq
  19965 \de    dfn Definition/description  (English)
  18392 \ps    pos Part of speech
  17049 \xv    exa Example (vernacular)
  17038 \xe    exe Example (English free translation)
  11123 \ck    not Check: Note to check something from Joe K.
  10829 \va    s*e Variant forms of headword
   8177 \ma    com Morphological analysis [at end, at subentry level, not \lx level] < \mr
   7080 \nqj   not Questions for further investigation: from Jeff
   6472 \pdl   com Paradigmatic label [\ro label w/ func title & postbase, or \pdv label to noun declensions] < \pd
   5557 \se    s*e Subentry
   4558 \et    ety Etymology (historical) [at end of entry and subentry]
   4400 \ro    ent Run-on: entry that only has a stem and no base variant
   3716 \syn   see Synonyms [right after \de or \de \cm] < \sy
   3426 \lx    ent Lexeme
   3398 \cit   com Historical citation
   2344 \cm    com Comment [entry, subentry, or example level]
   2258 \see   see See: "see also" another part of the dictionary
   2110 \xr    see Cross-reference {or possibly example (regional language free translation)?}
   2099 \pdv   s*e Paradigmatic form: conjugated/declined
   2054 \sse   s*e Sub-subentry
   1982 \pde   dfn Paradigmatic form English translation
   1575 \st    com {Stem: Underlying form of shortened word} {not editing status!}
   1536 \al    dfn Also: additional definition
    835 \cf    Confer/cross-reference to other headwords [at end of entry and subentry]
    777 \nd    Noun derivative {not discourse note!}
    757 \sc    Scientific name
    448 \lit   Literally < \lt
    207 \ssse  Sub-sub-subentry
     86 \id    {Idiom}
     48 \nt    Notes
     22 \nqa   Questions for further investigation: from April
     18 \nqs   Questions for further investigation: from Sperry
     17 \ant   Antonym
     10 \sssse Sub-sub-sub-subentry
      8 \hdr   {Subentry header: for lists of pronouns, etc.}
      6 \????  {Corrupted tag?}
      6 \      {Unknown tag}
      2 \new   {Note: new entry}
      2 \get   {Note: need to get info}
      1 \ssssse Sub-sub-sub-sub-subentry!

Varieties:
    K       Koniag
        AP      Alaska Peninsula
        PERRY   Perryville
        KOD     Kodiak
    C       Chugach
        KP      Kenai Peninsula
        PWS     Prince William Sound
'''

import codecs
import re
from collections import Counter

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
import django
django.setup()


NOTE_TAGS = {
    'nqq': 'Joe Kwaraceius:',
    'nqj': 'Jeff Leer:',
    'nqa': 'April Laktonen Counceller:',
    'nqs': 'Sperry Ash:',
    'zzz': 'XXX:',
    'ck': 'to check:',

    'cm': 'note:',
    # 'et': 'etymology:',
    'lit': 'literally:',
    'ma': 'analysis:',
    'st': 'underlying form:',
    'cf': 'cf.',
    'see': 'see',
}

EXPLANATIONS = {
    'va': 'variant of',
    'syn': 'synonym of',
    'ant': 'antonym of',
    'xr': 'referenced in',
}

VARIETIES = {
    'K': 'Koniag (includes Kodiak and Alaska Peninsula)',
    'AP': 'Alaska Peninsula',
    'PERRY': 'Perryville',
    'KOD': 'Kodiak and adjoining islands',
    'C': 'Chugach (includes Kenai Peninsula and Prince William Sound)',
    'KP': 'Kenai Peninsula',
    'PWS': 'Prince William Sound',
    '': 'other varieties',
}


class Entry(object):
    def __init__(self, entry='', main_entry=None):
        self.entry = entry
        self.defn = ''
        self.etymology = ''
        self.pos = ''
        self.root = ''
        self.source = 'A/SD'
        self.source_info = ''
        self.varieties = []
        self.examples = []
        self.main_entry = main_entry
        self.notes = ''
        self.comments = ''
        self.model = None


class Example(object):
    def __init__(self, vernacular=''):
        self.vernacular = vernacular
        self.english = ''
        self.source = 'A/SD'
        self.source_info = ''
        self.varieties = []
        self.notes = ''
        self.comments = ''
        self.model = None


class FieldGenerator(object):
    def __init__(self, lines):
        self.iter = iter(lines)
        self.done = False
        self.nextline = next(self.iter)[:-1]
        self.line_num = 0
        self.next()

    def next(self):
        if self.done:
            raise StopIteration

        line = self.nextline

        while True:
            try:
                self.nextline = next(self.iter)[:-1]
                self.line_num += 1
            except StopIteration:
                self.done = True
                break
            if '\t' in self.nextline:
                break
            elif self.nextline.strip():
                line = u'{} {}'.format(line, self.nextline.strip())

        self.key, self.value = line.split('\t', 1)
        while self.key.startswith('\\'):
            self.key = self.key[1:]


def parse_combined(infile):
    '''Top-level parsing function.'''

    entries = []
    examples = []

    garbage = Counter()

    f = FieldGenerator(infile)

    while f.key != 'lx':
        garbage[f.key] += 1
        f.next()

    while True:
        try:
            parse_entry(0, f, entries, examples, garbage)
        except StopIteration:
            break

    for k, count in garbage.most_common():
        print(u'{:7d} {}'.format(count, k))

    print('{} entries'.format(len(entries)))
    print('{} examples'.format(len(examples)))

    return entries, examples


def parse_entry(sublevel, f, entries, examples, garbage, main_entry=None):
    r'''\lx, \se, \sse, etc.'''

    word, number = extract_superscript(f.value)
    letter = u'a'
    entry = Entry(entry=ortho_fix(word), main_entry=main_entry)
    entries.append(entry)
    f.next()

    while True:
        if f.key == 'lx':
            return
        elif f.key == 's' * (len(f.key) - 1) + 'e':
            newsub = len(f.key) - 1
            if newsub > sublevel:
                # subentry of this one
                parse_entry(newsub, f, entries, examples, garbage, main_entry=entry)
            else:
                return
        elif f.key == 'dl':
            entry.varieties.extend(parse_varieties(f.value))
            f.next()
        elif f.key == 'so':
            entry.source_info = extend_source_info(entry.source_info, f.value)
            f.next()
        elif f.key == 'et':
            entry.etymology = extend_source_info(entry.etymology, f.value)
            f.next()
        elif f.key in ('nqq', 'nqj', 'nqa', 'nqs', 'zzz', 'ck'):
            if f.value.strip():
                note = u'{} {}'.format(NOTE_TAGS[f.key], f.value.strip())
                entry.notes = u'\n'.join((entry.notes, note)) if entry.notes else note
            f.next()
        elif f.key in ('cm', 'lit', 'ma', 'st', 'cf', 'see'):
            if f.value.strip():
                note = u'{} {}'.format(NOTE_TAGS[f.key], f.value.strip())
                entry.comments = u'\n'.join((entry.comments, note)) if entry.comments else note
            f.next()
        elif f.key == 'ps':
            if entry.pos:
                # Create a new entry for each new definition or part of speech.
                # We only keep the word, pos, definition, and root; everything
                # else (variants, etc.) would be shown more than once if we
                # copied it over.
                new_entry = Entry(entry.entry, main_entry=entry.main_entry)
                new_entry.defn = entry.defn
                new_entry.root = entry.root
                entries.append(new_entry)
                entry = new_entry
            entry.pos = f.value
            f.next()
        elif f.key in ('de', 'al'):
            if entry.defn:
                if number:
                    entry.defn = u'.'.join((number + letter, entry.defn.split('.')[1]))
                    letter = unichr(ord(letter) + 1)
                new_entry = Entry(entry.entry, main_entry=entry.main_entry)
                new_entry.pos = entry.pos
                new_entry.root = entry.root
                entries.append(new_entry)
                entry = new_entry
            if number:
                add_letter = u'' if letter == u'a' else letter
                entry.defn = u'. '.join((number + add_letter, f.value))
            else:
                entry.defn = f.value
            f.next()
        elif f.key == 'sc':
            note = u'(scientific name: {})'.format(f.value)
            entry.defn = u' '.join((entry.defn, note)) if entry.defn else note
            f.next()
        elif f.key == 'xv':
            parse_example(f, examples, garbage, entry)
        elif f.key == 'cit':
            parse_example(f, examples, garbage, entry, citation=True)
        elif f.key in ('va', 'syn', 'ant', 'xr'):
            parse_variant(f, entries, examples, garbage, f.key, entry)
        elif f.key in ('pdl', 'nd'):
            parse_derivative(f, entries, examples, garbage, f.key, entry)
        else:
            # if f.key in ('ro', 'pde', 'xe'):
            #     print('! garbage {}: {}'.format(f.key, f.line_num))
            garbage[f.key] += 1
            f.next()


def extract_superscript(word):
    match = re.search(ur'\$(\d*)$', word)
    if match:
        group = match.groups()[0]
        if group:
            number = group
        else:
            number = None
        word = re.sub(ur'\$(\d*)$', u'', word)
    else:
        number = None

    return word, number


def ortho_fix(word):
    return word[:1] + word[1:].replace(u'ř', u'R')


def parse_example(f, examples, garbage, entry, citation=False):
    example = Example(vernacular=f.value)
    examples.append(example)
    entry.examples.append(example)
    f.next()

    while True:
        if f.key == 'xe':
            example.english = f.value
            f.next()
            return
        elif f.key == 'dl':
            example.varieties.extend(parse_varieties(f.value))
            f.next()
        elif f.key == 'so':
            example.source_info = extend_source_info(example.source_info, f.value)
            f.next()
        elif f.key in ('cm', 'lit'):
            if f.value.strip():
                note = u'{} {}'.format(NOTE_TAGS[f.key], f.value.strip())
                example.comments = (
                    u'\n'.join((example.comments, note))
                    if example.comments else
                    note
                )
            f.next()
        elif f.key in ('nqq', 'nqj', 'nqa', 'nqs', 'zzz', 'ck'):
            if f.value.strip():
                note = u'{} {}'.format(NOTE_TAGS[f.key], f.value.strip())
                example.notes = u'\n'.join((example.notes, note)) if example.notes else note
            f.next()
        elif f.key == 'va' and not citation:
            parse_example_variant(f, examples, garbage, entry)
        elif f.key == 'cit' and citation:
            return
        else:
            # print('! {} ended by {}: {}'.format('cit' if citation else 'xv', f.key, f.line_num))
            return


def parse_variant(f, entries, examples, garbage, band, main_entry):
    variant = Entry(entry=ortho_fix(f.value), main_entry=main_entry)
    variant.defn = u'({}: `{}`)'.format(EXPLANATIONS[band], main_entry.entry)
    if band in ('syn', 'ant', 'va'):
        variant.pos = main_entry.pos
    defn_is_explanation = True
    pos_from_main = True
    entries.append(variant)
    f.next()

    while True:
        if f.key == 'va' and band == 'va':
            return
        elif f.key in ('ps', 'de', 'al') and band != 'xr':
            return
        elif f.key == 'st' and band != 'va':
            return
        elif f.key == 'lx' or f.key == 's' * (len(f.key) - 1) + 'e':
            return
        elif f.key in ('de', 'al'):
            if not defn_is_explanation:
                new_variant = Entry(variant.entry, main_entry=variant.main_entry)
                new_variant.pos = variant.pos
                new_variant.root = variant.root
                entries.append(new_variant)
                variant = new_variant
            variant.defn = f.value
            defn_is_explanation = False
            f.next()
        elif f.key == 'ps':
            if variant.pos and not pos_from_main:
                new_variant = Entry(variant.entry, main_entry=variant.main_entry)
                new_variant.defn = variant.defn
                new_variant.root = variant.root
                entries.append(new_variant)
                variant = new_variant
            variant.pos = f.value
            pos_from_main = False
            f.next()
        elif f.key == 'dl':
            variant.varieties.extend(parse_varieties(f.value))
            f.next()
        elif f.key == 'so':
            variant.source_info = extend_source_info(variant.source_info, f.value)
            f.next()
        elif f.key in ('nqq', 'nqj', 'ck'):
            if f.value.strip():
                note = u'{} {}'.format(NOTE_TAGS[f.key], f.value.strip())
                variant.notes = u'\n'.join((variant.notes, note)) if variant.notes else note
            f.next()
        elif f.key in 'ma' or \
                (f.key == 'cm' and band == 'va') or \
                (f.key == 'see' and band == 'xr'):
            if f.value.strip():
                note = u'{} {}'.format(NOTE_TAGS[f.key], f.value.strip())
                variant.comments = u'\n'.join((variant.comments, note)) if variant.comments else note
            f.next()
        elif f.key == 'xv' and band not in ('syn', 'ant'):
            parse_example(f, examples, garbage, variant)
        elif f.key == 'va':
            parse_variant(f, entries, examples, garbage, 'va', variant)
        else:
            # garbage['v/' + f.key] += 1
            # print('! {} ended by {}: {}'.format(band, f.key, f.line_num))
            return


def parse_example_variant(f, examples, garbage, entry):
    variant = Example(vernacular=f.value)
    examples.append(variant)
    entry.examples.append(variant)
    f.next()

    while True:
        if f.key in ('va', 'xe', 'xv'):
            return
        elif f.key == 'dl':
            variant.varieties.extend(parse_varieties(f.value))
            f.next()
        elif f.key == 'so':
            variant.source_info = extend_source_info(variant.source_info, f.value)
            f.next()
        elif f.key in ('nqq', 'nqj', 'nqs', 'nqa', 'zzz', 'ck'):
            if f.value.strip():
                note = u'{} {}'.format(NOTE_TAGS[f.key], f.value.strip())
                variant.notes = u'\n'.join((variant.notes, note)) if variant.notes else note
            f.next()
        else:
            # print('! xv/va ended by {}: {}'.format(f.key, f.line_num))
            return


def parse_derivative(f, entries, examples, garbage, band, main_entry):
    derivative = Entry(entry='', main_entry=main_entry)
    derivative.defn = u'{} of `{}`'.format(f.value, main_entry.entry)
    entries.append(derivative)
    f.next()

    while True:
        if f.key in ('pdl', 'nd', 'lx', 'et') or f.key == 's' * (len(f.key) - 1) + 'e':
            return
        elif f.key in ('ro', 'pdv'):
            if derivative.entry:
                # Create a new entry for each new word, definition, or part of speech.
                # We only keep the word, pos, definition, and root; everything
                # else (variants, etc.) would be shown more than once if we
                # copied it over.
                new_derivative = Entry(derivative.entry, main_entry=derivative.main_entry)
                new_derivative.pos = derivative.pos
                new_derivative.defn = derivative.defn
                new_derivative.root = derivative.root
                entries.append(new_derivative)
                derivative = new_derivative
            derivative.entry = ortho_fix(f.value)
            f.next()
        elif f.key == 'ps':
            if derivative.pos:
                new_derivative = Entry(derivative.entry, main_entry=derivative.main_entry)
                new_derivative.defn = derivative.defn
                new_derivative.root = derivative.root
                entries.append(new_derivative)
                derivative = new_derivative
            derivative.pos = f.value
            f.next()
        elif f.key in ('de', 'pde', 'al'):
            if derivative.defn:
                new_derivative = Entry(derivative.entry, main_entry=derivative.main_entry)
                new_derivative.pos = derivative.pos
                new_derivative.root = derivative.root
                entries.append(new_derivative)
                derivative = new_derivative
            derivative.defn = f.value
            f.next()
        elif f.key == 'sc':
            note = u'(scientific name: {})'.format(f.value)
            derivative.defn = u' '.join((derivative.defn, note)) if derivative.defn else note
            f.next()
        elif f.key == 'dl':
            derivative.varieties.extend(parse_varieties(f.value))
            f.next()
        elif f.key == 'so':
            derivative.source_info = extend_source_info(derivative.source_info, f.value)
            f.next()
        elif f.key in ('nqq', 'nqj', 'nqa', 'nqs', 'zzz', 'ck'):
            if f.value.strip():
                note = u'{} {}'.format(NOTE_TAGS[f.key], f.value.strip())
                derivative.notes = u'\n'.join((derivative.notes, note)) if derivative.notes else note
            f.next()
        elif f.key in ('lit', 'ma', 'st'):
            if f.value.strip():
                note = u'{} {}'.format(NOTE_TAGS[f.key], f.value.strip())
                derivative.comments = u'\n'.join((derivative.comments, note)) if derivative.comments else note
            f.next()
        # elif f.key == 'xv':
        #     parse_example(f, examples, garbage, derivative)
        elif f.key == 'cit':
            parse_example(f, examples, garbage, derivative, citation=True)
        elif f.key in ('va', 'syn', 'ant', 'xr'):
            parse_variant(f, entries, examples, garbage, f.key, derivative)
        else:
            # print('! {} ended by {}: {}'.format(band, f.key, f.line_num))
            return


def parse_varieties(value):
    '''
    >>> parse_varieties('C KOD [N]')
    [(u'C', u''), (u'KOD', u'[N]')]
    >>> parse_varieties('AP ~(???)~ C')
    [(u'AP', u'~(???)~'), (u'C', u'')]
    >>> parse_varieties('StL [K]')
    [(u'', u'StL'), (u'K', u'')]
    >>> parse_varieties('C [except not]')
    [(u'C', u'[except not]')]
    '''
    result = []
    detail = u''
    tokens = unicode(value).split()
    while tokens:
        while tokens and remove_punct(tokens[-1]) not in VARIETIES:
            detail = u' '.join((tokens.pop(), detail))
        if tokens:
            result.append((remove_punct(tokens.pop()), detail.strip()))
            detail = u''

    if detail.strip():
        result.append((u'', detail.strip()))

    result.reverse()
    return result


def remove_punct(token):
    return u''.join(c for c in token if c.isalnum())


def extend_source_info(old, new):
    if old and new:
        return u'; '.join((old, new))
    elif new:
        return new
    else:
        return old


def populate_db(entries, examples):
    from dictionary.models import Source
    try:
        Source.objects.get(abbrev='A/SD')
    except Source.DoesNotExist:
        Source(
            abbrev='A/SD',
            description='Joe Kwaraceius, Jeff Leer, et al., '
                        'Alutiiq/Sugpiaq Dictionary, 2018 (preprint)',
        ).save()

    for i, entry in enumerate(entries):
        insert_entry(entry)
        if i % 1000 == 0:
            print(u'entry {} ({})'.format(i, entry.entry).encode('utf-8'))
    for i, example in enumerate(examples):
        insert_example(example)
        if i % 1000 == 0:
            print('example {}'.format(i))


def insert_entry(entry):
    from dictionary.models import Entry as EntryModel
    from dictionary.models import EntryExampleInfo, EntryVarietyInfo
    if entry.model is not None or not entry.entry:
        return
    m = entry.model = EntryModel(
        entry=entry.entry,
        defn=entry.defn,
        pos=entry.pos,
        root=entry.root,
        source=lookup_source(entry.source),
        source_info=entry.source_info,
        etymology=entry.etymology,
        notes=entry.notes,
        comments=entry.comments,
    )
    m.save()
    for example in entry.examples:
        insert_example(example)
        if example.model:
            EntryExampleInfo(
                entry=m,
                example=example.model,
            ).save()
    for main, detail in entry.varieties:
        variety_model = get_variety_model(main)
        EntryVarietyInfo(
            entry=m,
            variety=variety_model,
            detail=detail,
        ).save()
    if entry.main_entry:
        insert_entry(entry.main_entry)
        if entry.main_entry.model:
            m.main_entry = entry.main_entry.model
            m.save()


def insert_example(example):
    from dictionary.models import Example as ExampleModel
    from dictionary.models import ExampleVarietyInfo
    if example.model is not None or not example.vernacular:
        return
    m = example.model = ExampleModel(
        vernacular=example.vernacular,
        english=example.english,
        source=lookup_source(example.source),
        source_info=example.source_info,
        notes=example.notes,
        comments=example.comments,
    )
    m.save()
    for main, detail in example.varieties:
        variety_model = get_variety_model(main)
        ExampleVarietyInfo(
            example=m,
            variety=variety_model,
            detail=detail,
        ).save()


def lookup_source(abbrev):
    from dictionary.models import Source
    return Source.objects.get(abbrev=abbrev)


def get_variety_model(abbrev):
    from dictionary.models import Variety
    try:
        return Variety.objects.get(abbrev=abbrev)
    except Variety.DoesNotExist:
        model = Variety(abbrev=abbrev, description=VARIETIES[abbrev])
        model.save()
        return model



if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print('Usage: {} <dict_file.mdf>'.format(sys.argv[0]))
        sys.exit(-2)

    with codecs.open(sys.argv[1], 'r', encoding='utf-8') as infile:
        entries, examples = parse_combined(infile)

    answer = raw_input('continue and populate database (y/n)? ')
    if answer.lower() in ('y', 'yes'):
        print('populating...')
        populate_db(entries, examples)
    else:
        print('canceled')
