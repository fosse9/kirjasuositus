import db


def get_books():
    sql = """
        SELECT books.id,
               books.title,
               books.author,
               users.id user_id,
               users.username
        FROM books
        JOIN users ON books.user_id = users.id
        ORDER BY books.id DESC
    """
    return db.query(sql)


def get_book(book_id):
    sql = """
        SELECT books.id,
               books.title,
               books.author,
               books.description,
               users.id user_id,
               users.username
        FROM books
        JOIN users ON books.user_id = users.id
        WHERE books.id = ?
    """

    result = db.query(sql, [book_id])
    return result[0] if result else None


def add_book(title, author, description, user_id):
    sql = """
        INSERT INTO books (title, author, description, user_id)
        VALUES (?, ?, ?, ?)
    """

    db.execute(sql, [title, author, description, user_id])
    return db.last_insert_id()


def update_book(book_id, title, author, description):
    sql = """
        UPDATE books
        SET title = ?, author = ?, description = ?
        WHERE id = ?
    """

    db.execute(sql, [title, author, description, book_id])


def remove_book(book_id):
    sql = "DELETE FROM books WHERE id = ?"
    db.execute(sql, [book_id])


def find_books(query):
    sql = """
        SELECT id, title, author
        FROM books
        WHERE title LIKE ?
           OR author LIKE ?
           OR description LIKE ?
        ORDER BY id DESC
    """

    like = "%" + query + "%"
    return db.query(sql, [like, like, like])