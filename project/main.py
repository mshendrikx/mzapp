import random
import os

from flask import Blueprint, render_template, request, flash, redirect, url_for
from sqlalchemy import and_
from werkzeug.security import generate_password_hash
from flask_login import login_required, current_user
from . import db
from .models import User, Updates
from common import update_countries, control_data
main = Blueprint("main", __name__)

@main.route("/")
def index():

    return render_template("index.html", user=current_user)

@main.route("/profile")
@login_required
def profile():

    return render_template("profile.html", current_user=current_user)


@main.route("/profile", methods=["POST"])
@login_required
def profile_post():

    password = request.form.get("password")
    repass = request.form.get("repass")
    name = request.form.get("name")
    email = request.form.get("email")

    if password != repass:
        flash("Password está diferente")
        flash("alert-danger")
        return redirect(url_for("main.profile"))

    if '@' not in email:
        flash("Entrar E-mail válido")
        flash("alert-danger")
        return redirect(url_for("main.profile"))
            
    if password != "":
        current_user.password = generate_password_hash(password, method="pbkdf2:sha256")

    if name != "":
        current_user.name = name
        
    current_user.email = email

    db.session.add(current_user)
    db.session.commit()

    return redirect(url_for("main.profile"))

@main.route("/configuration")
@login_required
def configuration():

    if current_user.admin == "":
        flash("Só administradores podem configurar.")
        flash("alert-danger")
        return redirect(url_for("main.index"))

    updates = Updates.query.order_by(Updates.id).all()
    
    return render_template(
        "configuration.html",
        current_user=current_user,
        updates=updates,
    )
    
@main.route("/run_update/<updateid>")
@login_required
def run_update(updateid):

    if current_user.admin == "X":
        # Atualizar dados de controle
        flash("Atualização iniciada")
        flash("alert-success")        
        
        if updateid == 1:
            control_data()
        elif updateid == 2:
            update_countries()

    else:
        flash("Somente administrador pode executar esta função")
        flash("alert-danger")

    return redirect(url_for("main.configuration"))

@main.route("/change_update/<updateid>")
@login_required
def change_update(updateid):

    if current_user.admin == "X":
        
        if updateid == 1:
            1 == 1
        # Atualizar dados de controle
        flash("Atualização iniciada")
        flash("alert-success")

    else:
        flash("Somente administrador pode executar esta função")
        flash("alert-danger")

    return redirect(url_for("main.configuration"))