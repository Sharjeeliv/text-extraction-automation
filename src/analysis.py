# First Party
import os
from collections import Counter
import json

from os.path import join as pjoin


# Third Party
import pandas as pd
import spacy

import nltk

import sys

# Local
from params import DELIM, PATH, DEFAULT

# Built-in rules
BLACKLIST_WORDS = {"continue", "cont.", "continued"}
KEYWORD_POS_TAGS = {'NOUN', 'PROPN', 'VERB', 'ADJ', 'ADV'}

# def get_data_folder():
#     # path of your data in same folder of main .py or added using --add-data
#     if getattr(sys, 'frozen', False):
#         data_folder_path = sys._MEIPASS
#     else:
#         data_folder_path = os.path.dirname(
#             os.path.abspath(sys.modules['__main__'].__file__)
#         )
#     return data_folder_path


from pathlib import Path

# bundle_dir = Path(__file__).parent
# corpus_path = f"{get_data_folder()}/en_core_web_sm"
# nlp = spacy.load(corpus_path)

# try:
#     nlp = spacy.load("en_core_web_sm")
# except OSError:
#     # this wont work because the user might not have python
#     os.system("python -m spacy download en_core_web_sm")
#     nlp = spacy.load("en_core_web_sm")


nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')


# *********************
# HELPER FUNCTIONS
# *********************
def gen_dataset():
    files = [f for f in os.listdir(PATH['LABELS']) 
             if os.path.isfile(os.path.join(PATH['LABELS'], f)) 
             and f.endswith('Extracted.txt')]
    raw = []
    for file in files:
        input_path = pjoin(PATH['LABELS'], file)
        with open(input_path) as f:
            title = f.readline().lower().strip()
            if title == "": continue
            text = f.read().lower().strip().replace('"', "'")
            
            end = text.strip().split("\n")[-1]
            end = end if len(end.split(" ")) < DEFAULT["MAX_LINE_SIZE"] and end[-1] != "." else "null"
            raw.append([file, title, end, text])

    data = pd.DataFrame(raw, columns=['File', 'Start_Title', 'End_Title', 'Text'])
    data.to_csv(pjoin(PATH['METRICS'], 'roi_dataset.csv'), index=False)
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


def score_keywords(tallies: pd.DataFrame):
    total_keyword_tallies = sum(tallies['keywords'], Counter())
    median_n_words = tallies['n_words'].median()

    # Filter and compute relative frequencies
    keywords_scores = {word: [count, round(count/median_n_words, 2)] 
                   for word, count in total_keyword_tallies.items() if count > 1}

    input_path = pjoin(PATH['METRICS'], 'title_keywords.json')
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
def analysis_entry( ):
    dataset = gen_dataset()
    tallies = tally_keywords(dataset)
    compute_constants(dataset, tallies)
    score_keywords(tallies)

if __name__ == '__main__':
    analysis_entry()
    