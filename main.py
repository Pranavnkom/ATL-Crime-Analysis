import functools

from flask import (
    Blueprint, flash, g, redirect, home_template, request, session, url_for
)

from flaskr.db import get_db

bp = Blueprint('main', __name__, url_prefix='/main')
