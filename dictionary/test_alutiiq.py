import unittest
import re

ENDING_TEST_CASES = [
    # Basic noun
    ("yaamaq", "n", "ABS:PL:UNPOSS", "yaamat"),
    ("yaamaq", "n", "ABS:DU:POSS1P:POSSSG", "yaamagka"),

    # Basic intransitive verbs
    ("silugluni", "vi", "1P:PL:PRES", "silugtukut"),
    ("tang'rlluni", "vi", "3P:CONJ:SG", "tang'rlluni"),
    ("nerluni", "vi", "3P:PRES:SG", "ner'uq"),
    ("nerluni", "vi", "3P:CONJ:SG", "nerluni"),
    ("aqum'aluni", "vi", "1P:PRES:SG", "aqum'agua(nga)"),

    # Basic transitive verbs
    ("nalluluku", "vt", "O3P:OSG:PRES:S1P:SSG", "nalluwaqa"),
    ("nalluluku", "vt", "O3P:OSG:PAST:S1P:SSG", "nalluk'gka"),
    ("qunuklluku", "vt", "O3P:OSG:PRES:S1P:SSG", "qunukaqa"),
    ("aplluku", "vt", "O3P:OSG:PRES:S1P:SSG", "aptaqa"),
    ("eglluku", "vt", "O3P:OSG:PRES:S1P:SSG", "egtaqa"),
    ("aplluku", "vt", "O3P:OSG:PAST:S1P:SSG", "ap'sk'gka"),
    ("eglluku", "vt", "O3P:OSG:PAST:S1P:SSG", "eg'sk'gka"),

    # Irregular nouns
    #("kuik", "n", "ERG:SG:UNPOSS", "kuigem"),  # CG p. 125
    #("suk", "n", "ERG:SG:UNPOSS", "suugem"),  # CG p. 139

    # Irregular intransitive verbs
    #("ell'uni", "vi", "3P:PRES:SG", "et'uq"),  # CG p. 128
    #("mill'uni", "vi", "3P:PRES:SG", "mit'uq"),  # CG p. 128

    # Tricky edge cases for intransitive verbs: apostrophe, -ng, voiceless r
    ("nauluni", "vi", "3P:PL:PRES", "nau'ut"),  # CG p.129
    ("qitengluni", "vi", "3P:PRES:SG", "qitenguq"),  # CG p. 131
    ("tengluni", "vi", "3P:PAST:SG", "tengellria"),  # CG p. 128
    ("ek'arlluni", "vi", "1P:PAST:SG", "ek'allrianga"),

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
    ("kuik", "n", "ABS:POSS3P:POSSSG:SG", "kui'a"),  # CG p. 142 -- also kuiga
    ("ciqlluaq", "n", "ABS:POSS3P:POSSSG:SG", "ciqllua'a"),  # CG p. 142
    ("erneq", "n", "ABS:PL:POSS3P:POSSSG", "erneri"),  # CG p. 143
    #("nuliq", "n", "ABS:POSS3P:POSSSG:SG", "nulira"),  # CG p. 143
]


class TestEndings(unittest.TestCase):
    pass


def add_test(args):
    root, pos, features, expected = args

    def check_ending(self):
        from alutiiq import get_endings_map
        self.assertEqual(get_endings_map(root, pos)[features], expected)

    check_ending.__name__ = re.sub('[^a-zA-Z_]', '_',
                                   'test_%s_%s_%s__%s' % args)
    setattr(TestEndings, check_ending.__name__, check_ending)


for args in ENDING_TEST_CASES:
    add_test(args)


if __name__ == '__main__':
    import nose
    nose.main()
