#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse

FEATURE_FIELD = 2


def main():
    args = parse_user_args()

    for i, line in enumerate(args.input):
        fields = line.strip().split(' ||| ')
        feats = fields[FEATURE_FIELD].split()

        feat_names = set([f[:-1] for f in feats if f.endswith('=')])
        for f in args.features:
            if f not in feat_names:
                sys.stderr.write("Warning: Feature '{}' not found in line {}\n"
                                 .format(f, i))

        scores = []
        keep = False
        name = args.new_name
        old_feats = []
        for feat in feats:
            if feat.endswith('='):
                if feat[:-1] in args.features:
                    keep = True
                    if not name:
                        name = feat[:-1]
            elif keep:
                scores.append(float(feat))
            if not keep:
                old_feats.append(feat)

        score = sum(scores)
        new_feat = '{}= {:.4f}'.format(name, score)
        fields[FEATURE_FIELD] = ' '.join([new_feat] + old_feats)
        args.output.write(' ||| '.join(fields) + '\n')


def parse_user_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', metavar='FILE', nargs='?',
                        type=argparse.FileType('r'), default=sys.stdin,
                        help='input n-best list, default: STDIN')
    parser.add_argument('-o', '--output', metavar='FILE', nargs='?',
                        type=argparse.FileType('w'), default=sys.stdout,
                        help='output n-best list, default: STDOUT')
    parser.add_argument('-f', '--features', metavar='FEATURE', nargs='+',
                        required=True,
                        help='features to merge')
    parser.add_argument('-n', '--new-name', metavar='STR',
                        help='name of a new feature')
    return parser.parse_args()


if __name__ == '__main__':
    main()
