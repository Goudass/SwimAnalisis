"""Dziennik treningowy — sesje, serie, powtórzenia (czas, HR, laktat)."""

from datetime import datetime

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import app, db
from app.models import TrainingBlock, TrainingRep, TrainingSession, User


def _is_training_role():
    return current_user.role.role_name in ("Trener", "Zawodnik", "Admin")


def _athletes_in_club():
    return (
        User.query.filter_by(club_id=current_user.club_id, id_role=3)
        .order_by(User.last_name, User.user_name)
        .all()
    )


def _can_view_session(session: TrainingSession) -> bool:
    if session.id_club != current_user.club_id:
        return False
    role = current_user.role.role_name
    if role in ("Trener", "Admin"):
        return True
    if role == "Zawodnik":
        return session.id_user == current_user.id_user
    return False


def _can_edit_session(session: TrainingSession) -> bool:
    return _can_view_session(session)


def _parse_time_input(raw):
    """Zwraca (time_seconds, formatted_time) lub (None, None)."""
    if raw is None:
        return None, None
    s = str(raw).strip()
    if not s:
        return None, None
    try:
        parts = s.split(":")
        if len(parts) == 2:
            minutes = int(parts[0])
            seconds = float(parts[1])
            if minutes >= 60:
                return None, None
            total = minutes * 60 + seconds
        else:
            total = float(parts[0])
        if total < 0:
            return None, None
        formatted = s
        return total, formatted
    except (ValueError, TypeError):
        return None, None


def _parse_int(raw):
    if raw is None or str(raw).strip() == "":
        return None
    try:
        return int(str(raw).strip())
    except ValueError:
        return None


def _parse_float(raw):
    if raw is None or str(raw).strip() == "":
        return None
    try:
        return float(str(raw).replace(",", ".").strip())
    except ValueError:
        return None


@app.route("/training")
@login_required
def training_list():
    if not _is_training_role():
        flash("Brak dostępu do dziennika treningowego.", "danger")
        return redirect(url_for("index"))

    q = TrainingSession.query.filter_by(id_club=current_user.club_id)
    if current_user.role.role_name == "Zawodnik":
        q = q.filter_by(id_user=current_user.id_user)
    sessions = q.order_by(TrainingSession.session_date.desc(), TrainingSession.id_session.desc()).limit(100).all()

    return render_template("training/list.html", sessions=sessions, title="Dziennik treningowy")


@app.route("/training/new", methods=["GET", "POST"])
@login_required
def training_new():
    if not _is_training_role():
        flash("Brak dostępu.", "danger")
        return redirect(url_for("index"))

    athletes = []
    if current_user.role.role_name in ("Trener", "Admin"):
        athletes = _athletes_in_club()

    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        if not title:
            flash("Podaj tytuł treningu.", "warning")
            return redirect(url_for("training_new"))

        if current_user.role.role_name == "Zawodnik":
            athlete_id = current_user.id_user
        else:
            athlete_id = _parse_int(request.form.get("athlete_id"))
            athlete = User.query.get(athlete_id)
            if not athlete or athlete.club_id != current_user.club_id or athlete.id_role != 3:
                flash("Wybierz zawodnika ze swojego klubu.", "danger")
                return redirect(url_for("training_new"))

        session_date_raw = request.form.get("session_date")
        try:
            session_date = datetime.strptime(session_date_raw, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            flash("Podaj poprawną datę.", "warning")
            return redirect(url_for("training_new"))

        training_type = (request.form.get("training_type") or "").strip() or None
        notes = (request.form.get("notes") or "").strip() or None

        session = TrainingSession(
            id_club=current_user.club_id,
            id_user=athlete_id,
            id_created_by=current_user.id_user,
            session_date=session_date,
            title=title,
            training_type=training_type,
            notes=notes,
        )
        db.session.add(session)
        db.session.commit()
        flash("Trening zapisany. Dodaj serie (np. 8×50) i uzupełnij powtórzenia.", "success")
        return redirect(url_for("training_session_detail", session_id=session.id_session))

    return render_template(
        "training/new.html",
        athletes=athletes,
        today=datetime.utcnow().date().isoformat(),
        title="Nowy trening",
    )


@app.route("/training/<int:session_id>")
@login_required
def training_session_detail(session_id):
    session = TrainingSession.query.get_or_404(session_id)
    if not _can_view_session(session):
        flash("Brak dostępu do tego treningu.", "danger")
        return redirect(url_for("training_list"))

    blocks = (
        TrainingBlock.query.filter_by(id_session=session.id_session)
        .order_by(TrainingBlock.id_block.asc())
        .all()
    )
    blocks_with_reps = []
    for b in blocks:
        reps = TrainingRep.query.filter_by(id_block=b.id_block).order_by(TrainingRep.rep_index.asc()).all()
        blocks_with_reps.append({"block": b, "reps": reps})

    return render_template(
        "training/session.html",
        session=session,
        blocks_with_reps=blocks_with_reps,
        can_edit=_can_edit_session(session),
        title=session.title,
    )


@app.route("/training/<int:session_id>/block/new", methods=["GET", "POST"])
@login_required
def training_block_new(session_id):
    session = TrainingSession.query.get_or_404(session_id)
    if not _can_edit_session(session):
        flash("Nie możesz edytować tego treningu.", "danger")
        return redirect(url_for("training_list"))

    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        if not title:
            flash("Podaj nazwę serii.", "warning")
            return redirect(url_for("training_block_new", session_id=session_id))

        distance_m = _parse_int(request.form.get("distance_m"))
        planned = _parse_int(request.form.get("planned_repetitions"))
        if not planned or planned < 1 or planned > 60:
            flash("Liczba powtórzeń: od 1 do 60.", "warning")
            return redirect(url_for("training_block_new", session_id=session_id))

        notes = (request.form.get("notes") or "").strip() or None
        block = TrainingBlock(
            id_session=session.id_session,
            title=title,
            distance_m=distance_m,
            planned_repetitions=planned,
            notes=notes,
        )
        db.session.add(block)
        db.session.flush()

        for i in range(1, planned + 1):
            db.session.add(TrainingRep(id_block=block.id_block, rep_index=i))
        db.session.commit()
        flash("Seria dodana — uzupełnij czasy, HR i laktat dla każdego powtórzenia.", "success")
        return redirect(url_for("training_session_detail", session_id=session_id))

    return render_template("training/block_new.html", session=session, title="Nowa seria")


@app.route("/training/block/<int:block_id>/delete", methods=["POST"])
@login_required
def training_block_delete(block_id):
    block = TrainingBlock.query.get_or_404(block_id)
    session = block.session
    if not _can_edit_session(session):
        flash("Brak uprawnień.", "danger")
        return redirect(url_for("training_list"))

    db.session.delete(block)
    db.session.commit()
    flash("Seria usunięta.", "info")
    return redirect(url_for("training_session_detail", session_id=session.id_session))


@app.route("/training/block/<int:block_id>/save-reps", methods=["POST"])
@login_required
def training_save_reps(block_id):
    block = TrainingBlock.query.get_or_404(block_id)
    session = block.session
    if not _can_edit_session(session):
        flash("Brak uprawnień.", "danger")
        return redirect(url_for("training_list"))

    reps = TrainingRep.query.filter_by(id_block=block_id).order_by(TrainingRep.rep_index.asc()).all()
    for rep in reps:
        prefix = f"rep_{rep.id_rep}_"
        t_raw = request.form.get(prefix + "time")
        ts, ft = _parse_time_input(t_raw)
        rep.time_seconds = ts
        rep.formatted_time = ft if ts is not None else ((t_raw or "").strip() or None)
        rep.heart_rate = _parse_int(request.form.get(prefix + "hr"))
        rep.lactate_mmol = _parse_float(request.form.get(prefix + "lactate"))
        note = (request.form.get(prefix + "note") or "").strip()
        rep.note = note or None

    db.session.commit()
    flash("Zapisano powtórzenia.", "success")
    return redirect(url_for("training_session_detail", session_id=session.id_session))


@app.route("/training/<int:session_id>/delete", methods=["POST"])
@login_required
def training_session_delete(session_id):
    session = TrainingSession.query.get_or_404(session_id)
    if not _can_edit_session(session):
        flash("Brak uprawnień.", "danger")
        return redirect(url_for("training_list"))

    db.session.delete(session)
    db.session.commit()
    flash("Trening usunięty.", "info")
    return redirect(url_for("training_list"))
