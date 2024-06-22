from warnings import filterwarnings as _filterwarnings

_filterwarnings(
    'ignore',
    message='Using slow pure-python SequenceMatcher. Install python-Levenshtein to remove this warning'
)

__version__ = "0.3.0"
