import secrets
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


@app.before_request
def set_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)


def check_csrf():
    token = session.get("csrf_token")
    if not token or request.form.get("csrf_token") != token:
        abort(403)


@app.route("/")
def index():
    all_books = books.get_books()
    return render_template("index.html", books=all_books)


@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)

    if not user:
        abort(404)

    user_books = books.get_user_books(user_id)
    return render_template("user.html", user=user, books=user_books)


@app.route("/book/<int:book_id>")
def show_book(book_id):
    book = books.get_book(book_id)

    if not book:
        abort(404)

    categories = books.get_book_categories(book_id)
    comments = books.get_comments(book_id)
    return render_template(
        "show_book.html",
        book=book,
        categories=categories,
        comments=comments
    )


@app.route("/create_comment/<int:book_id>", methods=["POST"])
def create_comment(book_id):
    require_login()
    check_csrf()

    book = books.get_book(book_id)

    if not book:
        abort(404)

    content = request.form.get("content", "").strip()

    if not 1 <= len(content) <= 5000:
        categories = books.get_book_categories(book_id)
        comments = books.get_comments(book_id)
        return render_template(
            "show_book.html",
            book=book,
            categories=categories,
            comments=comments,
            errors=["VIRHE: kommentin tulee olla 1-5000 merkkiä."]
        ), 400

    books.add_comment(book_id, session["user_id"], content)
    return redirect("/book/" + str(book_id) + "#comments")


@app.route("/find_book")
def find_book():
    query = request.args.get("query", "").strip()
    category_ids = list(dict.fromkeys(request.args.getlist("category_ids")))
    categories = books.get_categories()

    errors = []

    if len(query) > 100:
        errors.append("VIRHE: hakusana saa olla enintään 100 merkkiä.")

    valid_categories = {str(category["id"]) for category in categories}

    if any(category_id not in valid_categories for category_id in category_ids):
        errors.append("VIRHE: valitse luokittelut annetuista vaihtoehdoista.")

    if errors:
        return render_template(
            "find_book.html",
            query=query,
            categories=categories,
            selected_categories=category_ids,
            results=[],
            errors=errors
        ), 400

    if query or category_ids:
        results = books.find_books(query, category_ids)
    else:
        results = []

    return render_template(
        "find_book.html",
        query=query,
        categories=categories,
        selected_categories=category_ids,
        results=results
    )


@app.route("/new_book")
def new_book():
    require_login()
    categories = books.get_categories()
    return render_template(
        "new_book.html",
        categories=categories,
        selected_categories=[]
    )


@app.route("/create_book", methods=["POST"])
def create_book():
    require_login()
    check_csrf()

    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    description = request.form.get("description", "").strip()
    category_ids = list(dict.fromkeys(request.form.getlist("category_ids")))
    categories = books.get_categories()

    errors = []

    if not 1 <= len(title) <= 100:
        errors.append("VIRHE: kirjan nimen tulee olla 1-100 merkkiä.")

    if not 1 <= len(author) <= 100:
        errors.append("VIRHE: kirjailijan nimen tulee olla 1-100 merkkiä.")

    if not 1 <= len(description) <= 5000:
        errors.append("VIRHE: kuvauksen tulee olla 1-5000 merkkiä.")

    valid_categories = {str(category["id"]) for category in categories}

    if not category_ids:
        errors.append("VIRHE: valitse vähintään yksi luokittelu.")
    elif any(category_id not in valid_categories for category_id in category_ids):
        errors.append("VIRHE: valitse luokittelut annetuista vaihtoehdoista.")

    if errors:
        return render_template(
            "new_book.html",
            categories=categories,
            selected_categories=category_ids,
            errors=errors
        ), 400

    book_id = books.add_book(
        title,
        author,
        description,
        session["user_id"],
        category_ids
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

    categories = books.get_categories()
    selected_categories = [
        str(category["id"]) for category in books.get_book_categories(book_id)
    ]
    return render_template(
        "edit_book.html",
        book=book,
        categories=categories,
        selected_categories=selected_categories
    )


@app.route("/update_book", methods=["POST"])
def update_book():
    require_login()
    check_csrf()

    book_id = request.form["book_id"]
    book = books.get_book(book_id)

    if not book:
        abort(404)

    if book["user_id"] != session["user_id"]:
        abort(403)

    if "cancel" in request.form:
        return redirect("/book/" + str(book_id))

    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    description = request.form.get("description", "").strip()
    category_ids = list(dict.fromkeys(request.form.getlist("category_ids")))
    categories = books.get_categories()

    errors = []

    if not 1 <= len(title) <= 100:
        errors.append("VIRHE: kirjan nimen tulee olla 1-100 merkkiä.")

    if not 1 <= len(author) <= 100:
        errors.append("VIRHE: kirjailijan nimen tulee olla 1-100 merkkiä.")

    if not 1 <= len(description) <= 5000:
        errors.append("VIRHE: kuvauksen tulee olla 1-5000 merkkiä.")

    valid_categories = {str(category["id"]) for category in categories}

    if not category_ids:
        errors.append("VIRHE: valitse vähintään yksi luokittelu.")
    elif any(category_id not in valid_categories for category_id in category_ids):
        errors.append("VIRHE: valitse luokittelut annetuista vaihtoehdoista.")

    if errors:
        return render_template(
            "edit_book.html",
            book=book,
            categories=categories,
            selected_categories=category_ids,
            errors=errors
        ), 400

    books.update_book(
        book_id,
        title,
        author,
        description,
        category_ids
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

    check_csrf()

    if "remove" in request.form:
        books.remove_book(book_id)
        return redirect("/")

    return redirect("/book/" + str(book_id))


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/create", methods=["POST"])
def create():
    check_csrf()

    username = request.form["username"].strip()
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if not username or not password1:
        flash("VIRHE: tunnus ja salasana vaaditaan")
        return redirect("/register")

    if len(username) > 30:
        flash("VIRHE: tunnus saa olla enintään 30 merkkiä")
        return redirect("/register")

    if len(password1) > 128 or len(password2) > 128:
        flash("VIRHE: salasana saa olla enintään 128 merkkiä")
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

    check_csrf()

    username = request.form["username"]
    password = request.form["password"]

    user_id = users.check_login(username, password)

    if user_id:
        session["user_id"] = user_id
        session["username"] = username
        session["csrf_token"] = secrets.token_hex(16)
        return redirect("/")

    flash("VIRHE: väärä tunnus tai salasana")
    return redirect("/login")


@app.route("/logout", methods=["POST"])
def logout():
    require_login()
    check_csrf()
    session.clear()
    return redirect("/")