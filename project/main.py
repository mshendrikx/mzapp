import random
import os

from flask import Blueprint, render_template, request, flash, redirect, url_for
from sqlalchemy import and_
from werkzeug.security import generate_password_hash
from flask_login import login_required, current_user
from . import db
from .models import User, Player

main = Blueprint("main", __name__)