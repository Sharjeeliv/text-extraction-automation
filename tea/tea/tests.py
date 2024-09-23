import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


R_SENTENCE = r"^(\w+\s\w+\s\w+\s?)((\w+|-)\s?)*"

# *********************
# HELPER FUNCTIONS
# *********************
def get_text(file1: str, file2: str):
    try:
        text1 = open(file1, 'r').read()
        text2 = open(file2, 'r').read()
    except FileNotFoundError as e:
        print(f"ERROR - File not found: {e}")
        return -1
    return text1, text2


# *********************
# MAIN SIMILARITY METHOD
# *********************
def tokenize(text: str, unit: str=None):
    if unit == 'line':
        text = re.sub(r'[\n\t\r]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        chunks, n = [], 100
        for i in range(0, len(text), n):
            chunk = text[i:i+n]
            chunks.append(chunk)
        return chunks
    elif unit == 'sentence': 
        text = re.sub(r'[\n\t\r]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.split('. ')
    return text.lower().split(' ')

def overlap_similarity(label: str, pred: str):
    
    text1, text2 = get_text(label, pred)
    words1 = tokenize(text1, 'sentence')
    words2 = tokenize(text2, 'sentence')

    # Print the excess number of lines in the prediction 
    # for i, w in enumerate(words2): 
    #     if w not in words1[-3:-1]: continue
    #     print(f"End: {i:5}\tExcess: {len(words2) - i:5}")
    #     break
    
    # Print the tokenization of the paragraph into lines
    # print(f"Words1: {len(words1)}")
    # for n, i in enumerate(words1): print(f"{n:3}: {i[:64]}...")

    words1, words2 = set(words1), set(words2)
    intersection = len(words1.intersection(words2))
    return intersection / len(words1)

# *********************
# TOKEN BASED METHODS
# *********************
def jaccard_similarity(label: str, pred: str):
    
    text1, text2 = get_text(label, pred)
    words1 = set(text1.lower().split(' '))
    words2 = set(text2.lower().split(' '))

    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))

    return intersection / union

def sorenson_dice_similarity(label: str, pred: str):

    text1, text2 = get_text(label, pred)
    words1 = set(text1.lower().split(' '))
    words2 = set(text2.lower().split(' '))

    intersection = len(words1.intersection(words2))
    return 2 * intersection / (len(words1) + len(words2))

def cos_similarity(label: str, pred: str):
    
    text1, text2 = get_text(label, pred)
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([text1, text2])
    return cosine_similarity(tfidf)[0][1]

def ngram_similarity(label: str, pred: str, n: int=3):
    
    text1, text2 = get_text(label, pred)
    ngram1 = [text1[i:i+n] for i in range(len(text1)-n+1)]
    ngram2 = [text2[i:i+n] for i in range(len(text2)-n+1)]
    
    intersection = len(set(ngram1).intersection(set(ngram2)))
    union = len(set(ngram1).union(set(ngram2)))
    return intersection / union
