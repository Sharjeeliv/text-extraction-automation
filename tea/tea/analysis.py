# First Party
import os
from os.path import join as pjoin
from collections import Counter
import json

# Third Party
import pandas as pd
import spacy

# Local
from .params import DELIM, PATH, DEFAULT

# Built-in rules
BLACKLIST_WORDS = {"continue", "cont.", "continued"}
KEYWORD_POS_TAGS = {'NOUN', 'PROPN', 'VERB', 'ADJ', 'ADV'}

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# *********************
# HELPER FUNCTIONS
# *********************
def get_files(path, label, exts):
    files = []
    for root, _, filenames in os.walk(path):
        for filename in filenames:
            if label not in filename: continue
            if filename.endswith(tuple(exts)):
                files.append(os.path.join(root, filename))
    return files

def gen_dataset(files, label, metric_path: str, label_path: str):
    raw = []
    for file in files:
        input_path = pjoin(label_path, file)
        with open(input_path) as f:
            title = f.readline().lower().strip()
            if title == "": continue
            text = f.read().lower().strip().replace('"', "'")
            
            end = text.strip().split("\n")[-1]
            end = end if len(end.split(" ")) < DEFAULT["MAX_LINE_SIZE"] and end[-1] != "." else "null"

            # Process filename
            file = file.replace(f"_{label}", "")
            file = os.path.basename(file)

            raw.append([file, title, end, text])

    data = pd.DataFrame(raw, columns=['File', 'Start_Title', 'End_Title', 'Text'])
    data.to_csv(pjoin(metric_path, 'roi_dataset.csv'), index=False)
    return data

 # https://saturncloud.io/blog/how-to-detect-and-exclude-outliers-in-a-pandas-dataframe/#:~:text=Interquartile%20Range%20(IQR),-The%20interquartile%20range&text=Any%20data%20point%20outside%20the,75th%20percentiles%20of%20the%20dataset.
def max_without_outliers(data, column=None, factor=1.5):
    
    # Extract series from DataFrame
    if isinstance(data, pd.DataFrame):
        if column is None: raise ValueError("Column name must be provided if data is a DataFrame")
        series = data[column]
    elif isinstance(data, pd.Series): series = data
    else: raise ValueError("Data must be a DataFrame or Series")

    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    upper_threshold = q3 + factor * iqr
    return upper_threshold

# *********************
# CORE ANALYSIS FUNCTIONS
# *********************
def tally_keywords(df: pd.DataFrame):
    n_words, keywords = [], []
    for title in df['Start_Title']:
        
        # Guard Clause
        if pd.isnull(title):
            n_words.append(0)
            keywords.append(Counter())
            continue
        n_words.append(len(title.split(DELIM['WORD'])))
        # Tally Keywords & Counter filters
        counts = Counter()

        for token in nlp(title):
            if token.pos_ not in KEYWORD_POS_TAGS: continue
            if token.text in {".", ",", ":", ";", "-"}: continue
            if token.text in BLACKLIST_WORDS: continue
            counts[token.text] += 1
        keywords.append(counts)
        
    tallies = pd.DataFrame({'n_words': n_words, 'keywords': keywords})
    return tallies


def score_keywords(tallies: pd.DataFrame, metric_path):
    total_keyword_tallies = sum(tallies['keywords'], Counter())
    median_n_words = tallies['n_words'].median()

    # Filter and compute relative frequencies
    keywords_scores = {word: [count, round(count/median_n_words, 2)] 
                   for word, count in total_keyword_tallies.items() if count > 1}

    input_path = pjoin(metric_path, 'title_keywords.json')
    with open(input_path, 'w') as f: json.dump(keywords_scores, f)
    return keywords_scores


def compute_constants(dataset, tallies):
    # We use higher factor to have a more lenient threshold -experimentally determined
    max_n_words = max_without_outliers(tallies, 'n_words', factor=2.5)
    text_lengths = [len(text) for text in dataset['Text']]
    text_lengths = pd.Series(text_lengths)
    max_section_size = round(max_without_outliers(text_lengths, factor=3.5) / 100)

    print(f"Number of Labels:   {dataset.shape[0]}")
    print(f"Max n_words:        {max_n_words}")
    print(f"Max section size:   {max_section_size}")

    DEFAULT['MAX_SECT_SIZE'] = max_section_size
    DEFAULT['MAX_LINE_SIZE'] = max_n_words

# *********************
# ENTRY FUNCTIONS
# *********************
def analysis_entry(labels_path, metric_path, label_word, exts=[".txt"]):
    print("Analyzing files...")
    files = get_files(labels_path, label_word, exts)
    dataset = gen_dataset(files, label_word, metric_path, labels_path)
    tallies = tally_keywords(dataset)
    compute_constants(dataset, tallies)
    score_keywords(tallies, metric_path)

if __name__ == '__main__':
    analysis_entry("/Users/sharjeelmustafa/Desktop/LABELS", "Extracted", [".txt"])
    