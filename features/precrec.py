from base import FeatureBase
from difflib import SequenceMatcher


class WordPrecisionAndRecall(FeatureBase):
    name = 'wprec'
    desc = 'word precision and recall'

    def run(self, trg, src):
        src_toks = src.split()
        trg_toks = trg.split()
        src_set = set(src_toks)
        prec = len([t for t in trg_toks if t in src_set]) / \
            float(len(trg_toks) + 1)
        trg_set = set(trg_toks)
        recl = len([t for t in src_toks if t in trg_set]) / \
            float(len(src_toks) + 1)
        return "WordPrecision= {:.4f} WordRecall= {:.4f}".format(prec, recl)
