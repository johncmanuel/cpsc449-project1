from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from internal.utils import get_env_var
from sqlalchemy.orm import DeclarativeBase

load_dotenv()


UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}


# Base class for all models. Define here to prevent circular imports
class Base(DeclarativeBase):
    pass


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB limit
app.config["SECRET_KEY"] = get_env_var("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = get_env_var("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app, model_class=Base)
