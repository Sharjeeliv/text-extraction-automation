import time
import os
from typing import List
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score
import matplotlib.pyplot as plt

import pandas as pd
from bs4 import BeautifulSoup

from params import PATH, DEFAULT


# *********************
# EXTRACT HELPER FUNCTIONS
# *********************
def convert_to_series(results: List) -> pd.Series:
    results = [float(value) for value in results]
    results.sort()
    results_series = pd.Series(results)
    return results_series


def metrics(results_series: pd.Series):
    if results_series is None: return None
    if results_series.empty: return None

    print(f"\n\033[93;1mSUMMARY STATISTICS\033[0m")
    print(f"Mean:       {round(results_series.mean(), 2):7.2f}")
    print(f"Median:     {results_series.median():7.2f}")
    print(f"Mode:       {results_series.mode().values[0]:7.2f}")
    print(f"Q1:         {results_series.quantile(0.25):7.2f}")
    print(f"Q3:         {results_series.quantile(0.75):7.2f}")
    print(f"Minimum:    {results_series.min():7.2f}")
    print(f"Maximum:    {results_series.max():7.2f}")

    # plt.plot(sorted(results_series))
    # plt.xlabel('File Index')
    # plt.ylabel('Overlap Coefficient (%)')
    # plt.title('Overlap Coefficient Score Distribution')
    # plt.show()

    a = results_series[results_series >= 90]
    b = results_series[results_series >= DEFAULT["SUCCESS_THRESHOLD"] * 100]

    print(f"Success Rate >= 90: {round(len(a) / len(results_series) * 100, 2):7.2f}%")
    print(f"Success Rate >= 70: {round(len(b) / len(results_series) * 100, 2):7.2f}%")

    # Machine learning metrics
    preds = [1 if score >= (DEFAULT["SUCCESS_THRESHOLD"] * 100) else 0 for score in results_series]
    labels = [1] * len(results_series)
    
    print()
    print(f"Accuracy:   {round(accuracy_score(labels, preds), 2):7.2f}")
    print(f"Precision:  {round(precision_score(labels, preds), 2):7.2f}")
    print(f"Recall:     {round(recall_score(labels, preds), 2):7.2f}")
    print(f"F1:         {round(f1_score(labels, preds), 2):7.2f}")


def plot(results_series: pd.Series):
    if results_series is None: return None
    if results_series.empty: return None

    plt.plot(results_series)
    plt.xlabel('File Index')
    plt.ylabel('Similarity (%)')
    plt.title('Extracted Text Similarity to Label')

    plt.grid(True)
    plt.show()

# *********************
# HELPER FUNCTIONS
# *********************
def html_to_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    text_content = soup.get_text()
    return text_content

def time_execution(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        m, s = divmod(execution_time, 60)
        ms = (execution_time - int(execution_time)) * 1000
        print(f"\033[91;1mEXECUTION TIME: {int(m):02}:{int(s):02}.{int(ms):03}\033[0m")
        return result
    return wrapper

# *********************
# MAIN FUNCTION
# *********************
# if __name__ == '__main__':
#     gen_dataset()
