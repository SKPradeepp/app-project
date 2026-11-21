"""Flask web interface for Tamil Movie & OTT Discovery Management System.
Run alongside the existing Tkinter app with: python app.py
Both interfaces use the same MySQL database and account password format.
"""
import hashlib
import hmac
import os
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for
from mysql.connector import IntegrityError
from database import initialize_database, fetch_all, execute

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-local-demo-secret")


def hash_password(password, salt=None):
    salt = salt or __import__("secrets").token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000).hex()
    return f"{salt}${digest}"


def verify_password(password, stored):
    try:
        salt, digest = stored.split("$", 1)
        actual = hash_password(password, salt).split("$", 1)[1]
        return hmac.compare_digest(actual, digest)
    except (ValueError, AttributeError):
        return False


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.context_processor
def inject_user():
    return {"current_user": session.get("full_name")}


@app.route("/")
def index():
    return redirect(url_for("dashboard" if "user_id" in session else "login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 6:
            flash("Enter all fields and use a password of at least 6 characters.", "danger")
        else:
            try:
                execute("INSERT INTO users(full_name,email,password_hash) VALUES(%s,%s,%s)",
                        (name, email, hash_password(password)))
                flash("Account created. You can now sign in.", "success")
                return redirect(url_for("login"))
            except IntegrityError:
                flash("That email address is already registered.", "danger")
            except Exception as exc:
                flash(f"Registration failed: {exc}", "danger")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        try:
            rows = fetch_all("SELECT * FROM users WHERE email=%s", (email,))
            if rows and verify_password(password, rows[0]["password_hash"]):
                session.clear()
                session["user_id"] = rows[0]["user_id"]
                session["full_name"] = rows[0]["full_name"]
                return redirect(url_for("dashboard"))
            flash("Invalid email or password.", "danger")
        except Exception as exc:
            flash(f"Could not sign in: {exc}", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    uid = session["user_id"]
    stats = {
        "movies": fetch_all("SELECT COUNT(*) AS n FROM movies")[0]["n"],
        "users": fetch_all("SELECT COUNT(*) AS n FROM users")[0]["n"],
        "watchlist": fetch_all("SELECT COUNT(*) AS n FROM watchlist WHERE user_id=%s", (uid,))[0]["n"],
        "watched": fetch_all("SELECT COUNT(*) AS n FROM watchlist WHERE user_id=%s AND status='Watched'", (uid,))[0]["n"],
        "planned": fetch_all("SELECT COUNT(*) AS n FROM watchlist WHERE user_id=%s AND status='Plan to Watch'", (uid,))[0]["n"],
    }
    recent = fetch_all("SELECT movie_id,title,genre,release_year,rating FROM movies ORDER BY movie_id DESC LIMIT 6")
    return render_template("dashboard.html", stats=stats, recent=recent)


@app.route("/movies")
@login_required
def movies():
    q = request.args.get("q", "").strip()
    genre = request.args.get("genre", "").strip()
    sql = "SELECT movie_id,title,language,genre,director,release_year,rating FROM movies WHERE 1=1"
    params = []
    if q:
        sql += " AND (title LIKE %s OR director LIKE %s OR cast_members LIKE %s)"
        params.extend([f"%{q}%"] * 3)
    if genre:
        sql += " AND genre=%s"
        params.append(genre)
    sql += " ORDER BY title"
    rows = fetch_all(sql, tuple(params))
    genres = fetch_all("SELECT DISTINCT genre FROM movies WHERE genre IS NOT NULL AND genre<>'' ORDER BY genre")
    return render_template("movies.html", movies=rows, genres=genres, q=q, selected_genre=genre)


@app.route("/movie/<int:movie_id>")
@login_required
def movie_detail(movie_id):
    rows = fetch_all("SELECT * FROM movies WHERE movie_id=%s", (movie_id,))
    if not rows:
        flash("Movie not found.", "danger")
        return redirect(url_for("movies"))
    in_list = fetch_all("SELECT watchlist_id,status FROM watchlist WHERE user_id=%s AND movie_id=%s",
                        (session["user_id"], movie_id))
    return render_template("movie_detail.html", movie=rows[0], in_list=in_list[0] if in_list else None)


@app.route("/watchlist/add/<int:movie_id>", methods=["POST"])
@login_required
def add_to_watchlist(movie_id):
    try:
        execute("INSERT INTO watchlist(user_id,movie_id) VALUES(%s,%s)", (session["user_id"], movie_id))
        flash("Movie added to your watchlist.", "success")
    except IntegrityError:
        flash("This movie is already in your watchlist.", "info")
    except Exception as exc:
        flash(f"Could not add movie: {exc}", "danger")
    return redirect(url_for("movie_detail", movie_id=movie_id))


@app.route("/movie/add", methods=["GET", "POST"])
@login_required
def add_movie():
    if request.method == "POST":
        try:
            data = movie_form_data(request.form)
            if not data[0]:
                raise ValueError("Movie title is required.")
            execute("""INSERT INTO movies(title,language,genre,director,cast_members,release_year,
                       duration_minutes,rating,synopsis) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)""", data)
            flash("Movie added to the catalogue.", "success")
            return redirect(url_for("movies"))
        except (ValueError, TypeError) as exc:
            flash(str(exc), "danger")
        except Exception as exc:
            flash(f"Could not save movie: {exc}", "danger")
    return render_template("movie_form.html", movie=None, page_title="Add a movie")


def movie_form_data(form):
    title = form.get("title", "").strip()
    year = int(form["release_year"]) if form.get("release_year", "").strip() else None
    duration = int(form["duration_minutes"]) if form.get("duration_minutes", "").strip() else None
    rating = float(form["rating"]) if form.get("rating", "").strip() else 0.0
    if not 0 <= rating <= 10:
        raise ValueError("Rating must be between 0 and 10.")
    return (title, form.get("language", "").strip() or "Tamil", form.get("genre", "").strip(),
            form.get("director", "").strip(), form.get("cast_members", "").strip(), year,
            duration, rating, form.get("synopsis", "").strip())


@app.route("/movie/edit/<int:movie_id>", methods=["GET", "POST"])
@login_required
def edit_movie(movie_id):
    rows = fetch_all("SELECT * FROM movies WHERE movie_id=%s", (movie_id,))
    if not rows:
        flash("Movie not found.", "danger")
        return redirect(url_for("movies"))
    movie = rows[0]
    if request.method == "POST":
        try:
            data = movie_form_data(request.form)
            if not data[0]:
                raise ValueError("Movie title is required.")
            execute("""UPDATE movies SET title=%s,language=%s,genre=%s,director=%s,cast_members=%s,
                       release_year=%s,duration_minutes=%s,rating=%s,synopsis=%s WHERE movie_id=%s""",
                    data + (movie_id,))
            flash("Movie updated successfully.", "success")
            return redirect(url_for("movie_detail", movie_id=movie_id))
        except (ValueError, TypeError) as exc:
            flash(str(exc), "danger")
        except Exception as exc:
            flash(f"Could not update movie: {exc}", "danger")
    return render_template("movie_form.html", movie=movie, page_title="Edit movie")


@app.route("/watchlist")
@login_required
def watchlist():
    rows = fetch_all("""SELECT w.watchlist_id,m.movie_id,m.title,m.genre,m.release_year,w.status
                        FROM watchlist w JOIN movies m ON w.movie_id=m.movie_id
                        WHERE w.user_id=%s ORDER BY w.added_at DESC""", (session["user_id"],))
    return render_template("watchlist.html", items=rows)


@app.route("/watchlist/watched/<int:item_id>", methods=["POST"])
@login_required
def mark_watched(item_id):
    execute("UPDATE watchlist SET status='Watched' WHERE watchlist_id=%s AND user_id=%s",
            (item_id, session["user_id"]))
    flash("Marked as watched.", "success")
    return redirect(url_for("watchlist"))


@app.route("/watchlist/remove/<int:item_id>", methods=["POST"])
@login_required
def remove_watchlist(item_id):
    execute("DELETE FROM watchlist WHERE watchlist_id=%s AND user_id=%s", (item_id, session["user_id"]))
    flash("Removed from your watchlist.", "info")
    return redirect(url_for("watchlist"))


if __name__ == "__main__":
    try:
        initialize_database()
        app.run(debug=True, use_reloader=False)
    except Exception as exc:
        print("Startup error:", exc)
        print("Check MySQL Server and the DB_CONFIG values in config.py.")
