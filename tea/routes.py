from flask import Blueprint, render_template, request, send_from_directory, url_for, flash

main = Blueprint('main', __name__)

@main.route("/info", methods=['GET', 'POST'])
def info():
    return render_template('info.html')

@main.route("/", methods=['GET', 'POST'])
def tea():
    texts   = request.files.getlist('texts[]')
    labels  = request.files.getlist('labels[]')
    words   = request.form.get('label_word')
    exts    = request.form.get('extensions')
    exts    = exts.split(' ') if exts else []

    print(len(texts), len(labels), words, exts)
    if len(texts) == 0 or len(labels) == 0 or len(exts) == 0 or not words:
        print("Missing required fields")
        flash("Please fill out all required fields", 'warning')
        return render_template('interface.html')
    

    return render_template('interface.html')