import sqlite3

from flask import Flask
from flask import abort, flash, redirect, render_template, request, session

import books
import config
import users


app = Flask(__name__)
app.secret_key = config.secret_key


def require_login():
    if "user_id" not in session:
        abort(403)


@app.route("/")
def index():
    all_books = books.get_books()
    return render_template("index.html", books=all_books)


@app.route("/book/<int:book_id>")
def show_book(book_id):
    book = books.get_book(book_id)

    if not book:
        abort(404)

    return render_template("show_book.html", book=book)


@app.route("/find_book")
def find_book():
    query = request.args.get("query", "")

    if query:
        results = books.find_books(query)
    else:
        results = []

    return render_template(
        "find_book.html",
        query=query,
        results=results
    )


@app.route("/new_book")
def new_book():
    require_login()
    return render_template("new_book.html")


@app.route("/create_book", methods=["POST"])
def create_book():
    require_login()

    title = request.form["title"].strip()
    author = request.form["author"].strip()
    description = request.form["description"].strip()

    if not title or not author or not description:
        abort(403)

    book_id = books.add_book(
        title,
        author,
        description,
        session["user_id"]
    )

    return redirect("/book/" + str(book_id))


@app.route("/edit_book/<int:book_id>")
def edit_book(book_id):
    require_login()

    book = books.get_book(book_id)

    if not book:
        abort(404)

    if book["user_id"] != session["user_id"]:
        abort(403)

    return render_template("edit_book.html", book=book)


@app.route("/update_book", methods=["POST"])
def update_book():
    require_login()

    book_id = request.form["book_id"]
    book = books.get_book(book_id)

    if not book:
        abort(404)

    if book["user_id"] != session["user_id"]:
        abort(403)

    title = request.form["title"].strip()
    author = request.form["author"].strip()
    description = request.form["description"].strip()

    if not title or not author or not description:
        abort(403)

    books.update_book(
        book_id,
        title,
        author,
        description
    )

    return redirect("/book/" + str(book_id))


@app.route("/remove_book/<int:book_id>", methods=["GET", "POST"])
def remove_book(book_id):
    require_login()

    book = books.get_book(book_id)

    if not book:
        abort(404)

    if book["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_book.html", book=book)

    if "remove" in request.form:
        books.remove_book(book_id)
        return redirect("/")

    return redirect("/book/" + str(book_id))


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"].strip()
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if not username or not password1:
        flash("VIRHE: tunnus ja salasana vaaditaan")
        return redirect("/register")

    if password1 != password2:
        flash("VIRHE: salasanat eivät ole samat")
        return redirect("/register")

    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        flash("VIRHE: tunnus on jo varattu")
        return redirect("/register")

    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    user_id = users.check_login(username, password)

    if user_id:
        session["user_id"] = user_id
        session["username"] = username
        return redirect("/")

    flash("VIRHE: väärä tunnus tai salasana")
    return redirect("/login")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")