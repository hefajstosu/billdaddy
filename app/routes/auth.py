from flask import Blueprint, redirect, render_template, request, session, url_for

from ..models import User

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form.get("username", "")).first()
        if user and user.check_password(request.form.get("password", "")):
            session["user_id"] = user.id
            return redirect(url_for("main.index"))
        return render_template("login.html", error="złe dane logowania")
    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
