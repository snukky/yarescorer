from base import FeatureBase
from difflib import SequenceMatcher


class LengthRatio(FeatureBase):
    name = 'ratio'
    desc = 'word length ratio'

    def run(self, trg, src):
        trg_size = len(trg.split()) + 1
        src_size = len(src.split()) + 1
        return "LenRatio= {:.4f}".format(trg_size / float(src_size))


class LengthRatioChars(FeatureBase):
    name = 'chratio'
    desc = 'character length ratio'

    def run(self, trg, src):
        trg_size = len(''.join(trg.split())) + 1
        src_size = len(''.join(src.split())) + 1
        return "CharRatio= {:.4f}".format(trg_size / float(src_size))
