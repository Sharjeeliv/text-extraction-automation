from flask import Blueprint, render_template, request, send_from_directory, url_for, flash
from .tea.params import PATH, init_path
from .tea import tea_api
import os

main = Blueprint('main', __name__)

@main.route("/info", methods=['GET', 'POST'])
def info():
    return render_template('info.html')

@main.route("/", methods=['GET', 'POST'])
def tea():
    # Retrieve user inputs
    texts   = request.files.getlist('texts[]')
    labels  = request.files.getlist('labels[]')
    word    = request.form.get('label_word')
    exts    = request.form.get('extensions')
    exts    = exts.split(' ') if exts else []

    print(len(texts), len(labels), word, exts)
    if not validated_inputs(texts, labels, word, exts): 
        return render_template('interface.html')

    save_files(texts, PATH['TEXTS'], exts)
    save_files(labels, PATH['LABELS'], exts)
    
    # batch and call api

    tea_api(word, exts)

    return render_template('interface.html')

# *********************
# HELPER FUNCTIONS
# *********************
def validated_inputs(texts, labels, word, exts):
    if len(texts) == 0:
        flash("Please provide a texts folder", 'danger')
        return False
    if len(labels) == 0:
        flash("Please provide a labels folder", 'danger')
        return False
    if len(exts) == 0:
        flash("Please provide at least one allowed extension", 'danger')
        return False
    if not word:
        flash("Please provide the label suffix word", 'warning')
        return False
    return True


def save_files(files, path, exts):
    if files is None: return -1
    for file in files:
        if os.path.splitext(file.filename)[1] not in exts: continue
        path = os.path.join(path, file.filename)
        open(path, 'w').write(file.read().decode('utf-8'))
    return 0