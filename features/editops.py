from base import FeatureBase
from difflib import SequenceMatcher


class FeatureEdits(FeatureBase):
    name = 'edits'
    desc = 'counts of word-based edit operations'

    def run(self, trg, src):
        matcher = SequenceMatcher(None, src.split(), trg.split())
        ops = [tag for tag, _, _, _, _ in matcher.get_opcodes()]
        return "EditIns= {} EditDel= {} EditSub= {}" \
            .format(ops.count('insert'),
                    ops.count('delete'),
                    ops.count('replace'))


class FeatureChars(FeatureBase):
    name = 'charedits'
    desc = 'counts of character-based edit operations'

    def run(self, trg, src):
        matcher = SequenceMatcher(None, src, trg)
        ops = [tag for tag, _, _, _, _ in matcher.get_opcodes()]
        return "CharIns= {} CharDel= {} CharSub= {}" \
            .format(ops.count('insert'),
                    ops.count('delete'),
                    ops.count('replace'))
