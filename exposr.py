#!/usr/bin/env python
import os
import sqlite3
from flask import Flask, render_template, Response, request, redirect, url_for, send_from_directory, session, g, abort, flash
from contextlib import closing
from processr import Processr
from viewr import Viewr
from werkzeug import secure_filename

# configuration
DATABASE = '/tmp/exposr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'oculonterrin'
PASSWORD = 'sleeponthefloor'
UPLOAD_FOLDER = 'static/uploads/'
# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

app.config['ALLOWED_EXTENSIONS'] = set(['mp4'])
def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def show_entries():
    cur = g.db.execute('select filename, description from entries order by id desc')
    entries = [dict(filename=row[0], description=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        g.db.execute('insert into entries (filename, description) values (?, ?)',
                     [filename, request.form['description']])
        g.db.commit()
        flash('New entry was successfully posted')
        return redirect(url_for('show_entries'))

@app.route('/process/<filename>')
def processr(filename):
    return Response(gen(Processr(app.config['UPLOAD_FOLDER']+filename)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/view/<filename>')
def viewr(filename):
    return Response(gen(Viewr(app.config['UPLOAD_FOLDER']+filename)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/viewerv/<filename>')
def viewerv(filename):
    return render_template('viewerv.html',filename=filename)
@app.route('/viewerp/<filename>')
def viewerp(filename):
    return render_template('viewerp.html',filename=filename)

def gen(video):
    while True:
        frame = video.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


if __name__ == '__main__':
    app.run( debug=True,threaded=True)
