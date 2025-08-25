from flask import Blueprint, jsonify, request
from flask_login import login_required
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..extensions import db, csrf
from ..models import Task, TaskHistory


api_bp = Blueprint("api", __name__)


@api_bp.route("/token", methods=["POST"])
@csrf.exempt
@login_required
def issue_token():
    from flask_login import current_user
    access_token = create_access_token(identity=str(current_user.id))
    return jsonify({"access_token": access_token})


@api_bp.route("/tasks/reorder", methods=["POST"])
@csrf.exempt
@jwt_required()
def reorder_task():
    data = request.get_json() or {}
    task_id = data.get("task_id")
    new_status = data.get("new_status")
    new_position = data.get("new_position")
    if not all([task_id, new_status, isinstance(new_position, int)]):
        return jsonify({"error": "Parâmetros inválidos"}), 400

    task = Task.query.get(task_id)
    try:
        user_id = int(get_jwt_identity())
    except Exception:
        return jsonify({"error": "Token inválido"}), 401
    if not task or task.owner_id != user_id:
        return jsonify({"error": "Tarefa não encontrada"}), 404

    old_status = task.status

    # Shift positions in target column
    siblings = Task.query.filter(Task.owner_id == task.owner_id, Task.status == new_status, Task.id != task.id).order_by(Task.position).all()
    for idx, sibling in enumerate(siblings, start=1):
        if idx >= new_position:
            sibling.position = idx + 1
    task.status = new_status
    task.position = new_position
    db.session.add(task)
    history = TaskHistory(task_id=task.id, actor_id=task.owner_id, action="moved", from_status=old_status, to_status=new_status, details=f"Posição {new_position}")
    db.session.add(history)
    db.session.commit()

    return jsonify({"success": True})
