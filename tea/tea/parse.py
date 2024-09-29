# A simplified and more logical parse layer
# Designed for extension to other file types

# First Party
import os
import re

# Third Party
from selectolax.parser import HTMLParser

from params import PATH
from utils import time_execution

# selenium parsing is too slow, and hand parsing is too hard
# Need to use more built-in features from selectolax

# *********************
# CONST & VARIABLES
# *********************
N_TOP_HTML_CHARS =  2325

# Generic Regex
rm_graphic = r"<DOCUMENT>\n?<TYPE>GRAPHIC(.*\n)*?<\/DOCUMENT>"
# rm_table = r"<table(.|\n)*?</table>"
rm_br = r"<br>"
rm_extranl = r"\n{3,}"
rm_empty = r"^\s*$"
rm_spaces = r" {2,}"
rm_sup = r"<sup[\w\n =\"-:;%>]*</sup>"
rm_extra = r"^[*|•|\s]*$"

# Conversion Regex
rm_start = r"<(div|tr|table)[\w\n =\"-:;%>]*>"
rm_end = r"</(div|tr|table)>"
rm_td_start = r"<td[\w\n =\"-:;%>]*>"
rm_td_end = r"</td>"

rm_font = r"^<font[\w\n =\"-:;%>]*>"
rm_font_end = r"</font>"


# *********************
# PARSE FUNCTIONS
# *********************
def parse_html(file_path) -> str:
    file_path = rename_file_extension(file_path, '.txt')
    # print(f"Processing: {file_path.split('/')[-1]}")
    
    output = "SEC_HTML\n"
    text = open(file_path, 'r').read()

    # Preprocess: Tag Removal
    text = re.sub(rm_graphic, "", text)
    text = re.sub(rm_br, "BREAK", text, flags=re.IGNORECASE)
    text = re.sub(rm_sup, "", text, flags=re.IGNORECASE)

    # Preprocess: Tag Conversion    
    text = re.sub(rm_start, "<p>", text, flags=re.IGNORECASE)
    text = re.sub(rm_end, "</p>", text, flags=re.IGNORECASE)
    text = re.sub(rm_td_start, "", text, flags=re.IGNORECASE)
    text = re.sub(rm_td_end, "", text, flags=re.IGNORECASE)

    # HTML Parsing
    html = HTMLParser(text)
    for element in html.css("p"):
        element_text = element.text(deep=True)

        # Remove same paragraph breaks
        element_text = re.sub("\t", " ", element_text)
        element_text = re.sub("\xa0", "\n", element_text)
        element_text = re.sub("\u2003", "  ", element_text)
        element_text = re.sub("\n", " ", element_text)

        # Remove Bullets
        element_text = re.sub(rm_extra, "", element_text)
        element_text = element_text.strip()
        if element_text:    output += element_text + "\n"
        else:               output += "\n"

    # Postprocess: Text Cleaning
    output = re.sub(rm_extranl, "\n\n", output)
    output = re.sub(rm_empty, "", output, flags=re.MULTILINE)
    output = re.sub(rm_spaces, " ", output)
    output = re.sub("BREAK", "\n", output, flags=re.IGNORECASE)

    return output


def parse_text(file_path)-> str:
    with open(file_path, 'r') as f: text = f.read()
    return text


def parse_files(files, output_folder):
    for file in files:
        text = "None"
        if is_html(file):   text = parse_html(file)
        else:               text = parse_text(file)

        # Write to output file
        full_name = os.path.basename(file)
        file_name = os.path.splitext(full_name)[0]
        output_file = os.path.join(output_folder, f"{file_name}.txt")
        with open(output_file, 'w') as f: f.write(text)


# *********************
# HELPER FUNCTIONS
# *********************
def rename_file_extension(file_path, ext):
    ext = ext if ext.startswith('.') else '.' + ext
    new_path = os.path.splitext(file_path)[0] + ext
    os.rename(file_path, new_path)
    return new_path


def is_html(path):
    with open(path, 'r') as f: 
        data = f.read(N_TOP_HTML_CHARS).lower()
        if data.find('<html>') != -1: return True
    return False


def get_files(path, label, exts):
    files = []
    for root, _, filenames in os.walk(path):
        for filename in filenames:
            if label in filename: continue
            if filename.endswith(tuple(exts)):
                files.append(os.path.join(root, filename))
    return files


# *********************
# MAIN FUNCTIONS
# *********************
@time_execution
def parse_entry(input_path:str, output_path: str, label=[], ext=[]):
    print("Parsing files...")
    files = get_files(input_path, label, ext)
    parse_files(files, output_path)


if __name__ == "__main__":
    input_folder = "/Users/sharjeelmustafa/Desktop/PARSE_TEST/IN"
    output_folder = "/Users/sharjeelmustafa/Desktop/PARSE_TEST/OUT"
    parse_entry(input_folder, output_folder, label='Extracted', ext=['.txt', '.html', '.htm'])
    