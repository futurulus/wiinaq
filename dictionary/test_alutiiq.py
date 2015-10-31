import unittest
import re

ENDING_TEST_CASES = [
    # Basic noun
    ("yaamaq", "n", "ABS:PL:UNPOSS", "yaamat"),
    ("yaamaq", "n", "ABS:DU:POSS1P:POSSSG", "yaamagka"),

    # Basic intransitive verbs
    ("silugluni", "vi", "1P:PL:POS:PRES", "silugtukut"),
    ("tang'rlluni", "vi", "3P:CONJ:POS:SG", "tang'rlluni"),
    ("nerluni", "vi", "3P:POS:PRES:SG", "ner'uq"),
    ("nerluni", "vi", "3P:CONJ:POS:SG", "nerluni"),
    ("agluni", "vi", "3P:POS:PRES:SG", "ag'uq"),
    ("agluni", "vi", "3P:CONJ:POS:SG", "agluni"),
    ("aqum'aluni", "vi", "1P:POS:PRES:SG", "aqum'agua(nga)"),
    ("aqumluni", "vi", "3P:POS:PRES:SG", "aqumuq"),  # CG p. 25

    # t-stem intransitive verbs
    ("tekilluni", "vi", "3P:POS:PRES:SG", "tekituq"),  # CG p. 25
    ("tekilluni", "vi", "3P:CONJ:POS:SG", "tekilluni"),
    ("tekilluni", "vi", "1P:POS:PRES:SG", "tekitua(nga)"),

    # q-stem transitive verbs
    ("caqlluni", "vi", "3P:CONJ:POS:SG", "caqlluni"),

    # Basic transitive verbs
    ("nalluluku", "vt", "O3P:OSG:POS:PRES:S1P:SSG", "nalluwaqa"),
    ("nalluluku", "vt", "O3P:OSG:PAST:POS:S1P:SSG", "nalluk'gka"),
    ("qunuklluku", "vt", "O3P:OSG:POS:PRES:S1P:SSG", "qunukaqa"),

    # t-stem transitive verbs
    ("aplluku", "vt", "O3P:OSG:POS:PRES:S1P:SSG", "aptaqa"),
    ("eglluku", "vt", "O3P:OSG:POS:PRES:S1P:SSG", "egtaqa"),
    ("aplluku", "vt", "O3P:OSG:PAST:POS:S1P:SSG", "ap'sk'gka"),
    ("eglluku", "vt", "O3P:OSG:PAST:POS:S1P:SSG", "eg'sk'gka"),

    # q-stem transitive verb
    ("quliyanguaqlluku", "vt", "O3P:OSG:POS:PRES:S1P:SSG", "quliyanguaqaqa"),
    ("quliyanguaqlluku", "vt", "CONJ:O3P:OSG:POS", "quliyanguaqlluku"),

    # -eq nouns
    ("nateq", "n", "LOC:SG:UNPOSS", "natermi"),
    ("nateq", "n", "ABS:POSS2P:POSSSG:SG", "natren"),
    ("nutek", "n", "LOC:SG:UNPOSS", "nutegmi"),
    ("nutek", "n", "ABS:POSS3P:POSSSG:SG", "nutga"),  # CG p. 143

    # Irregular nouns
    ("kuik", "n", "ERG:SG:UNPOSS", "kuigem"),  # CG p. 125
    ("suk", "n", "ABS:SG:UNPOSS", "suk"),  # CG p. 139
    ("suk", "n", "ERG:SG:UNPOSS", "suugem"),  # CG p. 139
    ("suk", "n", "ABS:PL:UNPOSS", "suuget"),
    ("suk", "n", "DAT:SG:UNPOSS", "sugmen"),
    ("suk", "n", "PER:SG:UNPOSS", "sugkun"),
    ("suk", "n", "PER:PL:UNPOSS", "sutgun"),
    ("piugta", "n", "PER:SG:UNPOSS", "piugtegun"),
    ("yaamaq", "n", "PER:SG:UNPOSS", "yaamagun"),
    ("suk", "n", "SG:SIM:UNPOSS", "sugt'stun"),

    # Irregular intransitive verbs
    ("ell'uni", "vi", "3P:POS:PRES:SG", "et'uq"),  # CG p. 128
    ("ell'uni", "vi", "3P:CONJ:POS:SG", "ell'uni"),
    ("ell'uni", "vi", "3P:PAST:POS:SG", "et'llria"),
    ("ell'uni", "vi", "1P:COND:POS:SG", "ellkuma"),
    ("ell'uni", "vi", "1P:CSEQ:POS:SG", "ellngama"),
    ("mill'uni", "vi", "3P:POS:PRES:SG", "mit'uq"),  # CG p. 128
    #("all'uni", "vi", "3P:POS:PRES:SG", "alltuq"),  # QANK p. 22
    ("ul'uni", "vi", "3P:CONJ:POS:SG", "ul'uni"),  # QANK p.23
    ("ul'uni", "vi", "3P:POS:PRES:SG", "uluq"),
    ("ul'uni", "vi", "3P:PAST:POS:SG", "ulellria"),
    ("ul'uni", "vi", "1P:COND:POS:SG", "ulkuma"),
    ("ul'uni", "vi", "1P:CSEQ:POS:SG", "ulngama"),

    # Tricky edge cases for intransitive verbs: apostrophe and linking y/w,
    # -ng, voiceless r
    ("nauluni", "vi", "3P:PL:POS:PRES", "nau'ut"),  # CG p.129
    ("tailuni", "vi", "3P:PL:POS:PRES", "taiyut"),  # Song: Tuntut Taiyut
    ("qawarniluni", "vi", "3P:POS:PRES:SG", "qawarniuq"),  # CG p. 25
    ("iqlluluni", "vi", "3P:POS:PRES:SG", "iqlluuq"),  # CG p. 25
    ("qitengluni", "vi", "3P:POS:PRES:SG", "qitenguq"),  # CG p. 131
    ("tengluni", "vi", "3P:PAST:POS:SG", "tengellria"),  # CG p. 128
    ("ek'arlluni", "vi", "3P:CONJ:POS:SG", "ek'arlluni"),
    ("ek'arlluni", "vi", "1P:PAST:POS:SG", "ek'allrianga"),
    ("ek'arlluni", "vi", "1P:COND:POS:SG", "ek'aquma"),

    # Locatives (not yet implemented)
    ##("acigpeni", "loc", "LOC:POSS2P:POSSSG:SG", "acigpeni"),  # CG p. 133
    ##("akuliit", "loc", "LOC:POSS3P:POSSPL:PL", "akuliit"),  # CG p. 133

    # Singulars of preinflected nouns
    ##("wiinga", "n", "ABS:SG:UNPOSS", "wi?"),  # CG p. 141
    #("neqet", "n", "ABS:SG:UNPOSS", "neqa"),  # CG p. 141

    # Dual possessed
    ("qayaq", "n", "ABS:DU:POSS3P:POSSSG", "qayak"),  # CG p. 139

    # Irregular possessed forms
    #("nuna", "n", "ABS:POSS3P:POSSSG:SG", "nunii"),  # CG p. 141
    #("piugta", "n", "ABS:POSS3P:POSSSG:SG", "piugtii"),  # CG p. 141
    #("saqul'aq", "n", "ABS:POSS3P:POSSSG:SG", "saqulgaa"),  # CG p. 142
    ("kuik", "n", "ABS:POSS3P:POSSSG:SG", "kuiga"),  # CG p. 142 -- kuiya? also kui'a
    ("ciqlluaq", "n", "ABS:POSS3P:POSSSG:SG", "ciqllua'a"),  # CG p. 142
    ("erneq", "n", "ABS:PL:POSS3P:POSSSG", "erneri"),  # CG p. 143
    #("nuliq", "n", "ABS:POSS3P:POSSSG:SG", "nulira"),  # CG p. 143

    # Consequential -te- + -ngama = -cama
    ("sun'arauluni", "vi", "1P:CSEQ:POS:SG", "sun'araungama"),
    ("aiwilluni", "vi", "1P:CSEQ:POS:SG", "aiwicama"),
    ("aiwilluku", "vt", "CSEQ:O3P:OSG:POS:S1P:SSG", "aiwicamgu"),

    # Conditional -te- + -kuma = -skuma
    ("tekilluni", "vi", "1P:COND:POS:SG", "tekiskuma"),
    # double vowel shortening in closed syllable
    ("liilluni", "vi", "3P:POS:PRES:SG", "liituq"),
    ("liilluni", "vi", "1P:COND:POS:SG", "liskuma"),
    ("liilluni", "vi", "1P:CSEQ:POS:SG", "liicama"),

    # Conditional -qe- + -kumgu = -q'gkumgu
    ("tuumiaqlluku", "vt", "COND:O3P:OSG:POS:S1P:SSG", "tuumiaq'gkumgu"),
    # but not past tense?
    #("tuumiaqlluku", "vt", "O3P:OSG:PAST:POS:S1P:SSG", "tuumiaq'gka"),

    # Negatives
    ("nalluluni", "vi", "3P:NEG:PRES:SG", "nallun'ituq"),
    ("nalluluni", "vi", "3P:CONJ:NEG:SG", "nallugkunani"),
    ("nalluluni", "vi", "2P:CONJ:NEG:SG", "nallugkunak"),
    ("nalluluni", "vi", "3P:CONJ:NEG:PL", "nallugkunateng"),

    ("agnguarluni", "vi", "3P:CONJ:NEG:SG", "agnguaqunani"),
    ("agluni", "vi", "3P:CONJ:NEG:SG", "agegkunani"),
    ("agatuluni", "vi", "3P:CONJ:NEG:SG", "agakinani"),

    ("nalluluku", "vt", "NEG:O3P:OSG:PAST:S1P:SSG", "nallun'llk'gka"),
    ("nalluluku", "vt", "NEG:O3P:OSG:PRES:S1P:SSG", "nallun'itaqa"),
    ("nalluluku", "vt", "CONJ:NEG:O3P:OSG", "nallugkunaku"),

    ("tangerlluku", "vt", "NEG:O3P:OSG:PRES:S1P:SSG", "tangen'itaqa"),

    ("miknani", "vi", "3P:POS:PRES:SG", "miktuq"),  # CG p. 25
    ("miknani", "vi", "3P:PAST:POS:SG", "mik'llnguq"),  # mikelnguq?
    ("cainani", "vi", "3P:POS:PRES:SG", "caituq"),
    ("cainani", "vi", "3P:PAST:POS:SG", "cailnguq"),
    ("cainani", "vi", "3P:INTERR:POS:SG", "caillta"),
    ("cainani", "vi", "3P:COND:POS:SG", "caillkan"),
    ("asiinani", "vi", "3P:POS:PRES:SG", "asiituq"),
    ("asiinani", "vi", "3P:PAST:POS:SG", "asilnguq"),
    ("asiinani", "vi", "3P:INTERR:POS:SG", "asillta"),
    ("asiinani", "vi", "3P:CONJ:POS:SG", "asiinani"),

    ("naninani", "vi", "3P:NEG:PRES:SG", "nanin'ituq"),
    ("akianani", "vi", "3P:NEG:PRES:SG", "akian'ituq"),

    ("piturniinani", "vi", "3P:NEG:PRES:SG", "piturnirtuq"),
]

POS_TEST_CASES = [
    ("wiinaq", "", "n"),
    ("silugluni", "", "vi"),
    ("qunuklluku", "", "vt"),
    ("ell'uni", "", "vi"),
    ("ul'uku", "", "vt"),
]

ROOT_TEST_CASES = [
    ("wiinaq", "", "wiinar"),
    ("silugluni", "", "silug"),
    ("qunuklluku", "", "qunuke"),
    ("kuik", "", "kuig"),
    ("suk", "", "su\\ug"),
    ("piugta", "", "piugte"),
]


class TestEndings(unittest.TestCase):
    pass


def add_ending_method(args):
    word, pos, features, expected = args

    def check_ending(self):
        from alutiiq import get_endings_map, get_root
        root = get_root(word)
        self.assertEqual(get_endings_map(root, pos)[features], expected)

    check_ending.__name__ = re.sub('[^a-zA-Z0-9_]', '_',
                                   'test_ending_%s_%s_%s__%s' % args)
    setattr(TestEndings, check_ending.__name__, check_ending)


def add_root_method(args):
    word, defn, expected = args

    def check_root(self):
        from alutiiq import get_root
        self.assertEqual(get_root(word, defn), expected)

    check_root.__name__ = re.sub('[^a-zA-Z0-9_]', '_',
                                   'test_root_%s_%s__%s' % args)
    setattr(TestEndings, check_root.__name__, check_root)


def add_pos_method(args):
    word, defn, expected = args

    def check_pos(self):
        from alutiiq import get_pos
        self.assertEqual(get_pos(word, defn), expected)

    check_pos.__name__ = re.sub('[^a-zA-Z0-9_]', '_',
                                   'test_pos_%s_%s__%s' % args)
    setattr(TestEndings, check_pos.__name__, check_pos)


for args in ENDING_TEST_CASES:
    add_ending_method(args)

for args in POS_TEST_CASES:
    add_pos_method(args)

for args in ROOT_TEST_CASES:
    add_root_method(args)


class TestPastMap(unittest.TestCase):
    def test_3p_sg(self):
        from alutiiq import PAST_MAP
        self.assertEqual(PAST_MAP['-llria'], '+[+t]uq')


if __name__ == '__main__':
    import nose
    nose.main()
