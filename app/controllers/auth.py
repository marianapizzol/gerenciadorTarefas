from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_wtf import FlaskForm
from bleach import clean
from ..extensions import db
from ..models import User


class RegisterForm(FlaskForm):
    username = StringField("Usuário", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Senha", validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField("Confirmar Senha", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Registrar")


class LoginForm(FlaskForm):
    username = StringField("Usuário", validators=[DataRequired()])
    password = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Entrar")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Senha Atual", validators=[DataRequired()])
    new_password = PasswordField("Nova Senha", validators=[DataRequired(), Length(min=6)])
    confirm_new = PasswordField("Confirmar Nova Senha", validators=[DataRequired(), EqualTo("new_password")])
    submit = SubmitField("Alterar Senha")


auth_bp = Blueprint("auth", __name__, template_folder="../templates/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("tasks.board"))
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User(username=clean(form.username.data.strip()), email=form.email.data.strip())
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Registro realizado com sucesso. Faça login.", "success")
            return redirect(url_for("auth.login"))
        except IntegrityError:
            db.session.rollback()
            flash("Usuário ou email já existem.", "danger")
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("tasks.board"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Login realizado com sucesso.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("tasks.board"))
        flash("Credenciais inválidas.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout realizado.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Senha atual incorreta.", "danger")
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Senha alterada com sucesso.", "success")
            return redirect(url_for("tasks.board"))
    return render_template("auth/change_password.html", form=form)


# OAuth routes (placeholders with instructions). Implementing full OAuth flow requires valid client IDs.
@auth_bp.route("/login/google")
def login_google():
    flash("OAuth Google não configurado neste ambiente. Defina GOOGLE_CLIENT_ID/SECRET.", "warning")
    return redirect(url_for("auth.login"))


@auth_bp.route("/login/github")
def login_github():
    flash("OAuth GitHub não configurado neste ambiente. Defina GITHUB_CLIENT_ID/SECRET.", "warning")
    return redirect(url_for("auth.login"))