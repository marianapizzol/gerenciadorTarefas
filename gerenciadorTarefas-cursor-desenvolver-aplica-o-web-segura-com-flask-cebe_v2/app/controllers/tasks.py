from flask import Blueprint, render_template, redirect, url_for, flash, request, Response, current_app, send_file
from flask_login import login_required, current_user
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf import FlaskForm
from sqlalchemy import and_
from io import BytesIO, StringIO
import csv
import re
from bleach import clean
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from ..extensions import db, mail
from ..models import Task, TaskHistory, get_next_position, User
from flask_mail import Message


class TaskForm(FlaskForm):
    title = StringField("Título", validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField("Descrição")
    status = SelectField("Status", choices=[("todo", "A Fazer"), ("doing", "Em Progresso"), ("done", "Concluído")])
    submit = SubmitField("Criar Tarefa")


tasks_bp = Blueprint("tasks", __name__, template_folder="templates/tasks")


@tasks_bp.route("/")
@login_required
def board():
    tasks_todo = Task.query.filter_by(owner_id=current_user.id, status="todo").order_by(Task.position).all()
    tasks_doing = Task.query.filter_by(owner_id=current_user.id, status="doing").order_by(Task.position).all()
    tasks_done = Task.query.filter_by(owner_id=current_user.id, status="done").order_by(Task.position).all()
    form = TaskForm()
    return render_template("tasks/board.html", tasks_todo=tasks_todo, tasks_doing=tasks_doing, tasks_done=tasks_done, form=form)


@tasks_bp.route("/tasks/create", methods=["POST"])
@login_required
def create_task():
    form = TaskForm()
    if form.validate_on_submit():
        title = clean(form.title.data.strip())
        description = clean(form.description.data or "")
        status = form.status.data
        position = get_next_position(current_user.id, status)
        task = Task(title=title, description=description, status=status, position=position, owner_id=current_user.id)
        db.session.add(task)
        db.session.flush()
        history = TaskHistory(task_id=task.id, actor_id=current_user.id, action="created", to_status=status, details=f"Tarefa '{title}' criada")
        db.session.add(history)
        db.session.commit()
        _process_mentions(description, task, current_user)
        flash("Tarefa criada.", "success")
    else:
        flash("Erro ao criar tarefa.", "danger")
    return redirect(url_for("tasks.board"))


def _process_mentions(text: str, task: Task, actor: User) -> None:
    if not text:
        return
    mentioned_usernames = set(re.findall(r"@([A-Za-z0-9_\.\-]+)", text))
    if not mentioned_usernames:
        return
    users = User.query.filter(User.username.in_(mentioned_usernames)).all()
    if not users:
        return
    with mail.connect() as conn:
        for user in users:
            msg = Message(subject=f"Você foi mencionado na tarefa #{task.id}", recipients=[user.email])
            msg.body = f"{actor.username} mencionou você na tarefa '{task.title}':\n\n{text}"
            try:
                conn.send(msg)
            except Exception:
                current_app.logger.warning("Falha ao enviar email para %s", user.email)
        if users:
            history = TaskHistory(task_id=task.id, actor_id=actor.id, action="mentioned", details=f"Mencionados: {', '.join(u.username for u in users)}")
            db.session.add(history)
            db.session.commit()


@tasks_bp.route("/export/tasks.csv")
@login_required
def export_csv():
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["ID", "Título", "Status", "Posição", "Criado em"])
    tasks = Task.query.filter_by(owner_id=current_user.id).order_by(Task.status, Task.position).all()
    for t in tasks:
        writer.writerow([t.id, t.title, t.status, t.position, t.created_at.isoformat()])
    output = si.getvalue()
    return Response(output, mimetype="text/csv; charset=utf-8", headers={"Content-Disposition": "attachment; filename=tasks.csv"})


@tasks_bp.route("/export/tasks.pdf")
@login_required
def export_pdf():
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, f"Tarefas de {current_user.username}")
    y -= 30
    c.setFont("Helvetica", 10)
    tasks = Task.query.filter_by(owner_id=current_user.id).order_by(Task.status, Task.position).all()
    for t in tasks:
        line = f"#{t.id} [{t.status}] ({t.position}) - {t.title}"
        if y < 50:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 10)
        c.drawString(50, y, line[:120])
        y -= 18
    c.showPage()
    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="tasks.pdf", mimetype="application/pdf")
