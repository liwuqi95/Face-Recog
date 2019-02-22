import functools
from werkzeug.exceptions import abort

from flask import (
    Blueprint, flash, g, redirect, request, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db
from app.ImageProcessing import save_thumbnail, draw_face_rectangle
import os

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    cursor = get_db().cursor()
    error = None

    if not username:
        error = 'Username is required.'
    elif not password:
        error = 'Password is required.'
    else:
        cursor.execute(
            'SELECT id FROM users WHERE username = %s', (username,)
        )
        if cursor.fetchone() is not None:
            error = 'User {0} is already registered.'.format(username)

    if error is None:
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)',
                       (username, generate_password_hash(password)))
        get_db().commit()
        return 'ok'

    return abort(404, error)


##TODO add more image types
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/upload', methods=['POST'])
def upload():
    error = None
    username = request.form['username']
    password = request.form['password']
    cursor = get_db().cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))

    user = cursor.fetchone()


    if user is None:
        error = 'User is not valid'
    elif not check_password_hash(user["password"], password):
        error = 'Incorrect password.'

    if error is not None:
        return abort(404, error)

    if 'file' not in request.files:
        error = 'You cannot upload empty file.'
    elif request.files['file'].filename == '':
        error = "Your file name is not valid."
    elif not allowed_file(request.files['file'].filename):
        error = "Your File format is not correct: {}".format(request.files['file'].filename)
    else:
        file = request.files['file']
        filename = file.filename
        cursor = get_db().cursor()
        cursor.execute('INSERT INTO images ( name, user_id) VALUES (%s, %s)', (filename, user['id']))
        id = cursor.lastrowid
        filename = str(id) + '.' + filename.rsplit('.', 1)[1].lower()
        file.save(os.path.join('app/images', filename))
        get_db().commit()
        save_thumbnail(filename, 200, 200)
        draw_face_rectangle(filename)
        return 'ok'

    return abort(404, error)
