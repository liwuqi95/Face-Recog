from flask import Flask
import os

app = Flask(__name__)

app.config.from_mapping(
    # a default secret that should be overridden by instance config
    SECRET_KEY='dev',
    # store the database in the instance folder
    DATABASE=os.path.join(app.instance_path, 'app.sqlite'),
)

try:
    os.makedirs(app.instance_path)
except OSError:
    pass


#init database
from app import db
db.init_app(app)

#init routes
from app import auth, image, api
app.register_blueprint(auth.bp)
app.register_blueprint(image.bp)
app.register_blueprint(api.bp)
