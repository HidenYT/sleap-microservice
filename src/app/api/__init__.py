from werkzeug.exceptions import HTTPException
from . import models

from flask import Blueprint

bp = Blueprint("api", __name__, url_prefix="/api")

from . import routers

from .error_handlers import handle_exception