from base import FeatureBase
from difflib import SequenceMatcher

import os
import sys


class TERStats(FeatureBase):
    name = 'ter'
    desc = 'TER statistics'

    def __init__(self):
        self.script = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            '../tools/runTER.py')
        self.stats = None

    def __del__(self):
        if self.stats:
            self.stats.close()

    def prepare(self, fsrc, ftrg, wdir):
        fout = os.path.join(wdir, 'terstats.txt')
        cmd = "{} -s {} -r {} --detailed > {}" \
            .format(self.script, fsrc, ftrg, fout)
        sys.stderr.write('Running: {}\n'.format(cmd))
        os.popen(cmd)
        if not os.path.exists(fout):
            raise
        self.stats = open(fout, 'r')
        self.stats.next()

    def run(self, trg, src):
        if not self.stats:
            raise Exception('No output with TER statistics')
        line = self.stats.next()
        if not line:
            raise Exception('No TER statistics for next line')
        stats = line.strip().split()[:-3]
        return "TERIns= {} TERDel= {} TERSub= {} TERShft= {} TERWdSh= {}" \
            .format(*stats)
            # " TERNumEr= {} TERNumWd= {} TER= {}".format(*stats)
