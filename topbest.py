#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

SCORE_FIELD = 3


def main():
    i = None
    text = None
    best = 0

    for line in sys.stdin:
        fields = [f.strip() for f in line.split('|||')]
        sid = fields[0]
        if i != sid:
            if i:
                sys.stdout.write(text + '\n')
        score = float(fields[SCORE_FIELD])
        if score > best or i != sid:
            i = sid
            text = fields[1]
            best = score
    sys.stdout.write(text + '\n')


if __name__ == '__main__':
    main()
