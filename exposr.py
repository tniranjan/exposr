#!/usr/bin/env python
import os
import sqlite3
from flask import Flask, render_template, Response, request, redirect, url_for, send_from_directory, session, g, abort, flash
from contextlib import closing
from processr import Processr
from viewr import Viewr
from werkzeug import secure_filename
from flask_jsglue import JSGlue

# create our little application :)
app = Flask(__name__)
app.config.from_object('config')
jsglue = JSGlue(app)

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
    cur = g.db.execute('select id, filename, description from entries order by id desc')
    entries = [dict(id=row[0], filename=row[1], description=row[2]) for row in cur.fetchall()]
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/remove/<id>')
def rementry(id):
    g.db.execute('delete from entries where id=' + id)
    g.db.commit()
    flash('Entry was successfully removed')
    return redirect(url_for('show_entries'))

@app.route('/process/<filename>/<runningFlag>')
def processr(filename,runningFlag):
    return Response(gen(Processr(app.config['UPLOAD_FOLDER']+filename),runningFlag),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/view/<filename>/<runningFlag>')
def viewr(filename,runningFlag):
    return Response(gen(Viewr(app.config['UPLOAD_FOLDER']+filename),runningFlag),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/viewer/<filename>')
def viewer(filename):
    return render_template('viewer.html',filename=filename)

def gen(video,runningFlag):
    while True:
        frame, isImage = video.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        if runningFlag=='1':
            break


if __name__ == '__main__':
    app.run( debug=True,threaded=True)
