from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory
)
from werkzeug.exceptions import abort

from app.auth import login_required
from app.db import get_db

import os

from app.ImageProcessing import save_thumbnail

bp = Blueprint('image', __name__)


@bp.route('/')
@login_required
def index():
    """Show all the images, most recent first."""
    cursor = get_db().cursor(dictionary=True)

    cursor.execute(
        'SELECT p.id as id, name, created, user_id, username'
        ' FROM images p JOIN users u ON p.user_id = u.id'
        ' WHERE p.user_id = %s '
        ' ORDER BY created DESC', (g.user['id'],)
    )

    images = cursor.fetchall()


    return render_template('image/index.html', images=images)


@bp.route('/images/<int:type>/<int:id>')
@login_required
def get_image(type, id):
    cursor = get_db().cursor(dictionary=True)

    cursor.execute(
        'SELECT p.id, name, user_id'
        ' FROM images p'
        ' WHERE p.id = %s',
        (id,))

    image = cursor.fetchone()

    if image is None:
        abort(404, "Image doesn't exist.".format(id))

    if image['user_id'] != g.user['id']:
        abort(403)

    dir = 'images'

    return send_from_directory(dir, str(image["id"]) + '.' + image["name"].rsplit('.', 1)[1])


def get_post(id, check_author=True):
    """Get a post and its author by id.
    Checks that the id exists and optionally that the current user is
    the author.
    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


##TODO add more image types
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == 'POST':
        error = None

        if 'file' not in request.files:
            error = 'You cannot upload empty file.'
        elif request.files['file'].filename == '':
            error = "Your file name is not valid."
        elif not allowed_file(request.files['file'].filename):
            error = "Your File format is not correct."
        else:
            file = request.files['file']
            filename = file.filename

            cursor = get_db().cursor()
            cursor.execute('INSERT INTO images ( name, user_id) VALUES (%s, %s)', (filename, g.user['id']))
            file.save(os.path.join('app/images', str(cursor.lastrowid) + '.' + filename.rsplit('.', 1)[1].lower()))
            get_db().commit()
            return redirect(url_for('image.index'))

        if error is not None:
            flash(error)

    return render_template('image/create.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ? WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    """Delete a post.
    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
