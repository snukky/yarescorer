#!/usr/bin/env python

import os
import sys
import subprocess
import argparse

FEATURE_FIELD = 2

METRICS = {
    'bleu': {
        'sctype': 'BLEU',
        'scconfig': 'case:true',
        'filter': r"sed -ur -e 's/^( *)(.)/\1\u\2/' -e 's/@@ //g'",
    },
    'bleu-lc': {
        'sctype': 'BLEU',
        'scconfig': 'case:false',
        'filter': r"sed -ur -e 's/@@ //g'",
    },
    'm2': {
        'sctype': 'M2SCORER',
        'scconfig': 'truecase:false,beta:0.5,max_unchanged_words:2,case:false',
        'filter': r"sed -ur -e 's/^( *)(.)/\1\u\2/' -e 's/@@ //g'",
    },
    'gleu': {
        'sctype': 'GLEU',
        'scconfig': 'lowercase:1,numrefs:4,smooth:1,debug:0',
        'filter': r"sed -ur -e 's/^( *)(.)/\1\u\2/' -e 's/@@ //g'",
    },
    'ter': {
        'sctype': 'TER',
        'scconfig': 'case:true',
        'filter': r"sed -ur -e 's/^( *)(.)/\1\u\2/' -e 's/@@ //g'",
    },
}


def main():
    args = parse_user_args()

    # Find executables
    extractor_exe = find_executable(args.bin_dir, 'extractor')
    kbmira_exe = find_executable(args.bin_dir, 'kbmira')

    # Create working directory
    if not os.path.exists(args.work_dir):
        os.mkdir(args.work_dir)

    # Read sparse features
    if args.sparse:
        sparse_feats = read_ini_features(args.sparse)

    # Get feature names and initial weights from N-best list
    init_weights = extract_features(
        args.nbest, skip_feats=sparse_feats, skip_prefix=args.sparse_prefix)

    # Run extractor
    metric = METRICS[args.metric]
    extractor_cmd = [
        extractor_exe,
        '--sctype',   metric['sctype'],
        '--scconfig', metric['scconfig'],
        '--scfile',   os.path.join(args.work_dir, 'scores.dat'),
        '--ffile',    os.path.join(args.work_dir, 'features.dat'),
        '--filter',   metric['filter'],
        '-r',         args.reference,
        '-n',         args.nbest
    ]

    sys.stdout.write("RUNNING: " + ' '.join(extractor_cmd))
    subprocess.call(extractor_cmd)

    # Write feature list
    feat_file = os.path.join(args.work_dir, 'init.dense')
    create_feature_list(feat_file, init_weights)

    # Run kbMIRA
    kbmira_cmd = [
        kbmira_exe,
        '--dense-init', feat_file,
        '--ffile',      os.path.join(args.work_dir, 'features.dat'),
        '--scfile',     os.path.join(args.work_dir, 'scores.dat'),
        '--sctype',     metric['sctype'],
        '--scconfig',   metric['scconfig'],
        '-o',           os.path.join(args.work_dir, 'mert.out'),
        '--iters',      str(args.iterations)
    ]

    sys.stdout.write("RUNNING: " + ' '.join(kbmira_cmd))
    subprocess.call(kbmira_cmd)

    # Read optimized weights
    mert_file = os.path.join(args.work_dir, 'mert.out')
    opt_weights = read_weights(mert_file, init_weights)

    # Generate rescore.ini
    ini_file = os.path.join(args.work_dir, 'rescore.ini')
    generate_ini(ini_file, opt_weights, sparse=sparse_feats)


def generate_ini(ini_file, opt_weights, sparse=None):
    with open(ini_file, 'w') as out:
        out.write('# Rescored feature weights\n')
        out.write('\n')
        out.write('[weight]\n')
        for (feat, ws) in opt_weights:
            weights = ' '.join(str(w) for w in ws)
            out.write('{} {}\n'.format(feat, weights))
        if sparse:
            for f in sparse:
                out.write('{}= {}\n'.format(f, sparse[f]))


def read_weights(mert_file, init_weights):
    opt_weights = []
    total = 0
    with open(mert_file) as inp:
        # Same structure as original weight list
        for (feat, weights) in init_weights:
            opt_weights.append([feat, []])
            for _ in weights:
                w = float(inp.readline().split()[1])
                opt_weights[-1][1].append(w)
                # Sum for normalization
                total += abs(w)
    # Normalize weights
    for (_, weights) in opt_weights:
        for i in range(len(weights)):
            weights[i] /= total
    return opt_weights


def create_feature_list(feat_file, weights):
    with open(feat_file, 'w') as out:
        for (feat, ws) in weights:
            for w in ws:
                out.write('{} {}\n'.format(feat, w))


def read_ini_features(ini_file):
    feats = {}
    with open(ini_file) as ini:
        for line in ini:
            f, w = line.strip().split(' ', 1)
            if f.endswith('='):
                f = f[:-1]
            feats[f] = float(w)
    if feats:
        sys.stdout.write("Found {} sparse features\n".format(len(feats)))
    else:
        sys.stderr.write(
            'Error: no sparse features found in "{}", empty file?\n'
            .format(ini_file))
        sys.exit(1)
    return feats


def extract_features(nbest_file,
                     init_weight=0,
                     skip_feats=None,
                     skip_prefix=None):
    init_weights = []
    fields = [f.strip() for f in open(nbest_file).readline().split('|||')]
    feats = fields[FEATURE_FIELD].split()
    for i in range(len(feats)):
        if feats[i].endswith('='):
            if skip_feats and feats[i][:-1] in skip_feats:
                continue
            if skip_prefix and feats[i].startswith(skip_prefix):
                continue
            n_weights = 0
            j = i + 1
            while j < len(feats):
                if feats[j].endswith('='):
                    break
                n_weights += 1
                j += 1
            init_weights.append([feats[i], [init_weight] * n_weights])
    return init_weights


def find_executable(bindir, name):
    exe = os.path.join(bindir, name)
    if not os.path.exists(exe):
        sys.stderr.write(
            'Error: cannot find executable "{}" in "{}", '
            'please specify --bin-dir\n'.format(exe, bindir))
        sys.exit(1)
    return exe


def parse_user_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--nbest', metavar='FILE', required=True,
                        help='n-best list augmented with new features')
    parser.add_argument('-r', '--reference', metavar='FILE',
                        help='reference', required=True)
    parser.add_argument('-w', '--work-dir', metavar='DIR', default='workdir',
                        help='optimizer working directory, default: %(default)s')
    parser.add_argument('-b', '--bin-dir', metavar='DIR', required=True,
                        help='directory containing kbmira, evaluator executables')
    parser.add_argument('-i', '--iterations', metavar='N', default=300, type=int,
                        help='number of optimizer iterations, default: %(default)s')
    parser.add_argument('-m', '--metric', default='bleu', choices=METRICS.keys(),
                        help='tuning metric, default: %(default)s')
    parser.add_argument('--sparse', metavar='FILE',
                        help='sparse feature weights')
    parser.add_argument('--sparse-prefix', metavar='STR',
                        help='prefix for sparse features')
    return parser.parse_args()


if __name__ == '__main__':
    main()
