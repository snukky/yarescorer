#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import math

from features import *


FEATURE_FIELD = 2


def get_feature_classes(cls=base.FeatureBase):
    subclasses = []
    for subcls in cls.__subclasses__():
        subclasses.append(subcls)
        subclasses.extend(get_feature_classes(subcls))
    return list(set(subclasses))


def has_file_based_features(fs):
    return any(callable(getattr(f, "prepare", None)) for f in fs)


FEATURES = {cls.name: cls.desc for cls in get_feature_classes()}

FEATURE_LIST = "Available features:\n" + \
    '\n'.join("{} - {}".format(f, FEATURES[f]) for f in FEATURES)


def main():
    args = parse_user_args()
    if args.show_features:
        print(FEATURE_LIST)
        exit()

    feats = [f() for f in get_feature_classes() if f.name in args.features]

    if has_file_based_features(feats):
        src_file, trg_file = create_parallel_files(
            args.nbest, args.source, args.work_dir)
        for f in feats:
            if callable(getattr(f, "prepare", None)):
                f.prepare(src_file, trg_file, args.work_dir)

    for trg, src, line in iterate_nbest_sentences(args.nbest, args.source):
        scores = [feat.run(trg, src) for feat in feats]
        if args.log:
            log_scores = []
            for elem in ' '.join(scores).split():
                if elem.endswith('='):
                    log_scores.append(elem)
                else:
                    val = float(elem)
                    log_scores.append(str(math.log(val)) if val else '-100.0')
            scores = log_scores
        fields = [f.strip() for f in line.split('|||')]
        fields[FEATURE_FIELD] += ' ' + ' '.join(scores)
        args.output.write(' ||| '.join(fields) + '\n')


def create_parallel_files(nbest, source, work_dir):
    if not os.path.exists(work_dir):
        os.mkdir(work_dir)
    src_file = os.path.join(work_dir, 'source.txt')
    trg_file = os.path.join(work_dir, 'target.txt')
    with open(src_file, 'w') as src_io, open(trg_file, 'w') as trg_io:
        for trg, src, _ in iterate_nbest_sentences(nbest, source):
            src_io.write(src + '\n')
            trg_io.write(trg + '\n')
    nbest.seek(0)
    source.seek(0)
    return src_file, trg_file


def iterate_nbest_sentences(nbest, source):
    sid = 0
    prev_sid = -1
    for line in nbest:
        line = line.rstrip('\n')
        sid, trg, _ = line.split(' ||| ', 2)
        sid = int(sid)
        if sid > prev_sid:
            src = source.next().strip()
        yield trg, src, line
        prev_sid = sid


def parse_user_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', metavar='FILE', required=True,
                        type=argparse.FileType('r'),
                        help='source sentences')
    parser.add_argument('-f', '--features', required=True, nargs='+',
                        metavar='FEATURE', choices=FEATURES.keys(),
                        help='features to be added to n-best list')
    parser.add_argument('-n', '--nbest', metavar='FILE', nargs='?',
                        type=argparse.FileType('r'), default=sys.stdin,
                        help='input n-best list, default: STDIN')
    parser.add_argument('-o', '--output', metavar='FILE', nargs='?',
                        type=argparse.FileType('w'), default=sys.stdout,
                        help='output n-best list with new features, default: STDOUT')
    parser.add_argument('-w', '--work-dir', metavar='DIR', default='featdir',
                        help='working directory, default: %(default)s')
    parser.add_argument('--log', action='store_true')
    parser.add_argument('--show-features', action='store_true',
                        help='list available features and exit')
    return parser.parse_args()


if __name__ == '__main__':
    main()
