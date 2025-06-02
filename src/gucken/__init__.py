from warnings import filterwarnings as _filterwarnings
_filterwarnings(
    'ignore',
    'Using slow pure-python SequenceMatcher. Install python-Levenshtein to remove this warning'
)
__version__ = "0.3.8"
