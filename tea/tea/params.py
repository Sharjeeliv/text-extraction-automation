import os
from pathlib import Path

# Uses the current file path to dynamically get the root path
_ROOT_PATH = Path(os.path.abspath(__file__)).parent.parent

# Define the paths using pathlib to handle cross-platform path structures
PATH = {
    "ROOT":     _ROOT_PATH,
    "TEXTS":    _ROOT_PATH / 'data' / 'texts',
    "RESULTS":  _ROOT_PATH / 'data' / 'results',
    "LABELS":   _ROOT_PATH / 'data' / 'label',
    "METRICS":  _ROOT_PATH / 'data' / 'metrics',
}

# Change the default parameters for each dataset
DEFAULT = {
    # Pre-nalysis Parameters
    "N_TOP_HTML_CHARS": 2325,   # Used to determine if HTML tag is within top n chars
    "N_TOP_TITLES": 20,         # Returns the top n titles from coarse extraction for fine-grain extraction
    "TOC_SKIP_CHARS": 10000,    # Skip the first n chars in the document to bypass the Table of Contents
    "MAX_SECT_SIZE": 673,       # Max size of a section (100 char units) based on pre-analysis
    "MAX_LINE_SIZE": 14,        # Max size of a line (word units) based on pre-analysis
    "SUCCESS_THRESHOLD": 0.7,   # Threshold for successful extraction
    # Title Word Parameters (differs per dataset)
    "REPEATABLE_KEYWORDS": ["advisory", "agreement", "agreements", "management"],
    "SPECIAL_PHRASES": ["investment advisory", "investment sub-advisory"]
}

DELIM = {
    "SENTENCE": ". ",
    "WORD": " "
}

def init_path():
    for _, value in PATH.items(): os.makedirs(value, exist_ok=True)

if __name__ == "__main__":
    init_path()
    for key, value in PATH.items(): print(f"{key}: {value}")
    