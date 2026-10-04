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


def get_user_books(user_id):
    sql = """
        SELECT id, title, author
        FROM books
        WHERE user_id = ?
        ORDER BY id DESC
    """
    return db.query(sql, [user_id])


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


def get_comments(book_id):
    sql = """
        SELECT comments.id,
               comments.content,
               comments.user_id,
               users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.book_id = ?
        ORDER BY comments.id
    """
    return db.query(sql, [book_id])


def add_comment(book_id, user_id, content):
    sql = """
        INSERT INTO comments (book_id, user_id, content)
        VALUES (?, ?, ?)
    """
    db.execute(sql, [book_id, user_id, content])


def get_categories():
    sql = "SELECT id, type, name FROM categories ORDER BY type, id"
    return db.query(sql)


def get_book_categories(book_id):
    sql = """
        SELECT categories.id, categories.type, categories.name
        FROM categories
        JOIN book_categories ON categories.id = book_categories.category_id
        WHERE book_categories.book_id = ?
        ORDER BY categories.type, categories.id
    """
    return db.query(sql, [book_id])


def set_book_categories(book_id, category_ids):
    sql = "DELETE FROM book_categories WHERE book_id = ?"
    db.execute(sql, [book_id])

    sql = "INSERT INTO book_categories (book_id, category_id) VALUES (?, ?)"
    for category_id in category_ids:
        db.execute(sql, [book_id, category_id])


def add_book(title, author, description, user_id, category_ids):
    sql = """
        INSERT INTO books (title, author, description, user_id)
        VALUES (?, ?, ?, ?)
    """

    db.execute(sql, [title, author, description, user_id])
    book_id = db.last_insert_id()
    set_book_categories(book_id, category_ids)
    return book_id


def update_book(book_id, title, author, description, category_ids):
    sql = """
        UPDATE books
        SET title = ?, author = ?, description = ?
        WHERE id = ?
    """

    db.execute(sql, [title, author, description, book_id])
    set_book_categories(book_id, category_ids)


def remove_book(book_id):
    sql = "DELETE FROM books WHERE id = ?"
    db.execute(sql, [book_id])


def find_books(query, category_ids=None):
    sql = """
        SELECT id, title, author
        FROM books
        WHERE (title LIKE ?
           OR author LIKE ?
           OR description LIKE ?
           OR EXISTS (
               SELECT 1
               FROM book_categories
               JOIN categories ON book_categories.category_id = categories.id
               WHERE book_categories.book_id = books.id
                 AND categories.name LIKE ?
           ))
    """

    like = "%" + query + "%"
    params = [like, like, like, like]

    for category_id in category_ids or []:
        sql += """
            AND EXISTS (
                SELECT 1
                FROM book_categories
                WHERE book_categories.book_id = books.id
                  AND book_categories.category_id = ?
            )
        """
        params.append(category_id)

    sql += " ORDER BY id DESC"
    return db.query(sql, params)