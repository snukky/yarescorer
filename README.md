# Yet Another N-Best list Re-Scorer

Scripts for n-best lists rescoring using kBMira.


Features:
* Optimization with kBMira
* Tuning metrics: TER, BLEU, M2
* Filters for post-processing during tuning (de-TC and de-BPE)
* Processing n-best lists with sparse features
* Extensible feature sets


## Requirements

Training a rescorer requires access to `kbmira` and `evaluator` executables
from [mosesdecoder](https://github.com/moses-smt/mosesdecoder).


## Usage

Training the rescorer:

```
./add-features.py -s dev.src -f edits ratio < dev.nbest > dev.nbest.with-features
./train.py -m BLEU --nbest dev.nbest.with-features -r dev.ref -w wdir -b path/to/moses/bin
```

Rescoring:

```
./add-features.py -s test.src -f edits ratio < test.nbest > test.nbest.with-features
./rescore.py -c wdir/rescore.ini < test.nbest.with-features > test.nbest.rescored
```

Implemented features:
* Length ratios
* Character and word-level edit features, i.e. number of insertions/deletions/substitutions
* TER statistics
* Word precision and recall

## Alternatives

* [N-best list re-scorer from Moses SMT](https://github.com/moses-smt/mosesdecoder/tree/master/scripts/nbest-rescore)
