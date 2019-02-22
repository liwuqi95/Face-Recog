import mysql.connector

import click
from flask import current_app, g
from flask.cli import with_appcontext

TABLES = {}

TABLES['users'] = (
    "CREATE TABLE `users` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `username` varchar(255) NOT NULL,"
    "  `password` varchar(255) NOT NULL,"
    "  PRIMARY KEY (`id`),"
    " UNIQUE (username)"
    ")")

TABLES['images'] = (
    "CREATE TABLE `images` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `user_id` int(11) NOT NULL,"
    "  `name` varchar(255) NOT NULL,"
    "   `created` DATETIME DEFAULT CURRENT_TIMESTAMP,"
    "  PRIMARY KEY (`id`), KEY `user_id` (`user_id`),"
    "  CONSTRAINT `image_usrfk_1` FOREIGN KEY (`user_id`) "
    "  REFERENCES `users` (`id`) ON DELETE CASCADE"
    ")")


def get_db():
    """return current connection or create a new one"""
    if 'db' not in g:
        g.db = mysql.connector.connect(user='root', password='ece1779pass',
                                       host='127.0.0.1',
                                       database='cloud')

    return g.db


def close_db(e=None):
    """Close mysql db connection"""
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    """Perform init db Mysql operations"""
    cursor = get_db().cursor()

    cursor.execute("DROP TABLE IF EXISTS images;")
    cursor.execute("DROP TABLE IF EXISTS users;")

    for table_name in TABLES:
        cursor.execute(TABLES[table_name])


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
