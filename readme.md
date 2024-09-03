# TEA - Text Extraction Automation

The TEA is designed to automatically extract sections of texts from documents for downstream use. Given the potentially large size and quantity of documents it limits itself to rule-based and performant techniques, making this tools valuable when large-scale compute is not available. To this end it uses a combination of label-tailored rules, regular expressions, and keyword matching to approximate sections of interest. As with all rule-based methods, it works best on simpler inputs (e.g., structured files) and performance decreases the more complex the extraction is.

Presently it lacks negative reinforcement and as such can't handle files that don't have sections of interests -it will simply return a random slice.

1. [Installation](#1-Installation)
2. [Usage](#2-Usage)
3. [Interface Requirements](#3-Interface-Requirements)
4. [Extending Instructions](#4-Extending-Instructions)
5. [Appendix](#5-Appendix)

## 1. Installation

1. **Clone the repository**

    ```bash
    git clone https://github.com/Sharjeeliv/GNN-Platform
    ```

2. **Install Python3 if needed**
    ```
    https://www.python.org/downloads/
    Developed on Version 3.12.1
    ```
3. **Install Conda if needed**
    ```bash
    https://docs.anaconda.com/miniconda/miniconda-install/
    ```
4. **Go to project folder**

5. **Install packages and activate environment**
    ```bash
    conda env create -f environment.yml
    conda activate tea
    ```
6. **Update params.py values as needed**

## 2. Usage

Example usage where target files are at "/Users/john/Documents/texts", corresponding labels are at "/Users/john/Documents/labels", each label end with _Extracted, and the targets files end in .txt, .html, and .htm.

Below is the corresponding command for the above situation, ensure that the command is executed from the src folder.

```bash
python main.py --texts "/Users/john/Documents/texts" --labels "/Users/john/Documents/labels" --ext .txt .html .htm --exclude Extracted -s _Extracted
```

For a list of input arguments use:
```bash
python3 main.py --help 
```

```
  -h, --help            show this help message and exit
  -t, --texts           path to directory containing files
  -e, --exclude         list of words to exclude files, e.g., label keyword
  -x, --ext             list of extensions allowed for files
  -l, --labels          path to directory containing labels
  -s, --label_suffix    label file suffix

  --analyze             flag which reruns analysis layer
  --log                 flag which prints log statements
  --test                flag which runs test functions, requires labels
```
