from datetime import datetime

from flask import Flask, jsonify, render_template, request
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError, PendingRollbackError

import ai_request
from data_models import db, Author, Book

# Create Instance of Flask application
app = Flask(__name__)

# Configure Database (SQLite file in data directory)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data/library.sqlite"

# Connect Flask app to Database via SQLAlchemy
db.init_app(app)

@app.route("/", methods=["GET", "POST"])
def home():
    """
    Home page route.
    Supports POST for sorting the books by title, author, year, or rating.
    Default GET lists all books.
    """
    if request.method == "POST":
        sort_by = request.form.get("options")
        if sort_by == "title":
            sort_by = getattr(Book, 'title', None)
        elif sort_by == "author":
            sort_by = getattr(Author, 'name', None)
        elif sort_by == "year":
            sort_by = getattr(Book, 'publication_year', None)
        elif sort_by == "rating":
            sort_by = getattr(Book, 'rating', None)
        descending = request.form.get("descending")
        if descending:
            books = db.session.query(Book.id, Book.isbn, Book.title,
                                     Author.name, Book.author_id,
                                     Book.publication_year, Book.rating).join(Author) \
                                        .order_by(desc(sort_by)).all()
        else:
            books = db.session.query(Book.id, Book.isbn, Book.title,
                                     Author.name, Book.author_id,
                                     Book.publication_year, Book.rating).join(Author) \
                                        .order_by(sort_by).all()
        return render_template("home.html", books=books)
    else:
        books = db.session.query(Book.id, Book.isbn, Book.title,
                                 Author.name, Book.author_id,
                                 Book.publication_year, Book.rating).join(Author).all()

        return render_template("home.html", books=books)

@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    """
    Route to add a new author (POST) or search authors (GET).
    On GET with 'name', returns matching authors as JSON.
    On POST, adds author to the database if valid.
    """
    if request.method == "GET":
        name = request.args.get("name", "")
        if name:
            authors = db.session.query(Author) \
                .filter(Author.name.contains('%' + name + '%')) \
                .all()
            output = []
            # Convert query results to dictionaries for JSON response
            for author in authors:
                author = dict({'name': author.name,
                               'birth_date': author.birth_date.strftime('%Y-%m-%d'),
                               'date_of_death': author.date_of_death.strftime('%Y-%m-%d')
                               if author.date_of_death else None})
                output.append(author)
            return jsonify(output), 200
        else:
            return render_template("add_author.html")
    # POST: add new author
    elif request.method == "POST":
        if not request.form["name"].strip() or not request.form["birthdate"]:
            return render_template("add_author.html", success=False,
                                   error="Please enter a name and birthdate!"), 401
        name = request.form["name"].strip()
        birthdate = datetime.strptime(request.form["birthdate"], "%Y-%m-%d")
        if request.form["date_of_death"]:
            date_of_death = datetime.strptime(request.form["date_of_death"], "%Y-%m-%d")
            author = Author(name=name, birth_date=birthdate, date_of_death=date_of_death)
        else:
            author = Author(name=name, birth_date=birthdate)
        try:
            db.session.add(author)
            db.session.commit()
            return render_template("add_author.html", success=True)
        except Exception as e:  # Catch all exceptions for debugging
            print(e.__class__())
            return render_template("add_author.html", success=False), 401

@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    """
    Route to add a new book (POST) or search books (GET).
    On GET with query params, returns matching books as JSON.
    On POST, adds book to the database if valid.
    """
    if request.method == "GET":
        title = request.args.get("title", "")
        year = request.args.get("year", "")
        isbn = request.args.get("isbn", "")
        rating = request.args.get("rating", "")
        if title:
            books = db.session.query(Book) \
                .filter(Book.title.contains('%' + title + '%')) \
                .all()
            output = []
            for book in books:
                book = dict({'title': book.title,
                             'year': book.publication_year,
                             'rating': book.rating})
                output.append(book)
            return jsonify(output), 200
        elif year:
            books = db.session.query(Book) \
                .filter(Book.publication_year.contains('%' + year + '%')) \
                .all()
            output = []
            for book in books:
                book = dict({'title': book.title,
                             'year': book.publication_year})
                output.append(book)
            return jsonify(output), 200
        elif isbn:
            books = db.session.query(Book) \
                .filter(Book.isbn.contains('%' + isbn + '%')) \
                .all()
            output = []
            for book in books:
                book = dict({'title': book.title,
                             'year': book.publication_year})
                output.append(book)
            return jsonify(output), 200
        elif rating:
            books = db.session.query(Book) \
                .filter(Book.rating.contains(rating)) \
                .all()
            output = []
            for book in books:
                book = dict({'title': book.title,
                             'year': book.publication_year})
                output.append(book)
            return jsonify(output), 200
        else:
            authors = db.session.query(Author).all()
            return render_template("add_book.html", authors=authors)
    # POST: add new book
    elif request.method == "POST":
        title = request.form["title"]
        year = request.form["year"]
        isbn = request.form["isbn"] if request.form["isbn"] else None
        author_id = request.form["author"]
        rating = request.form["rating"]
        try:
            book = Book(title=title, publication_year=year,
                        isbn=isbn, author_id=author_id, rating=rating)
            db.session.add(book)
            db.session.commit()
            authors = db.session.query(Author).all()
            return render_template("add_book.html",
                                   success=True, authors=authors)
        except IntegrityError:
            db.session.rollback()
            authors = db.session.query(Author).all()
            return render_template("add_book.html",
                                   success=False, authors=authors,
                                   error="Entry already exists, check ISBN and/or whole book to assure uniqueness!"
                                   ), 401
        except PendingRollbackError:
            db.session.rollback()
            authors = db.session.query(Author).all()
            return render_template("add_book.html",
                                   success=False, authors=authors,
                                   error="Could not add book to database"
                                   ), 401
        except Exception as e:  # Catch all exceptions for debugging
            db.session.rollback()
            authors = db.session.query(Author).all()
            return render_template("add_book.html",
                                   success=False, error="Something went wrong:",
                                   authors=authors), 401

@app.route('/add_recommendation', methods=['POST'])
def add_recommendation():
    """
    Route to add an AI recommendation via POST.
    Adds new author/book as needed based on form data.
    """
    books = db.session.query(Book.id, Book.isbn, Book.title,
                             Author.name, Book.author_id, Book.publication_year,
                             Book.rating).join(Author).all()
    if request.method != "POST":
        return render_template("add_recommendation.html", books=books)
    author = Author.query.filter(Author.name == request.form["author"]).first()
    if not author:
        birth_date = datetime.strptime(request.form["birthday"], "%Y-%m-%d")
        if request.form["died"]:
            date_of_death = datetime.strptime(request.form["died"], "%Y-%m-%d")
            author = Author(name=request.form["author"],
                            birth_date=birth_date, date_of_death=date_of_death)
            db.session.add(author)
            db.session.commit()
        else:
            author = Author(name=request.form["author"], birth_date=birth_date)
            db.session.add(author)
            db.session.commit()
    try:
        new_author = Author.query.filter(Author.name == author.name).first()
        book = Book(isbn=request.form["isbn"], title=request.form["title"],
                    publication_year=request.form["year"],
                    author_id=new_author.id)
        db.session.add(book)
        db.session.commit()
        new_books = db.session.query(Book.id, Book.isbn, Book.title,
                                    Author.name, Book.author_id, Book.publication_year,
                                    Book.rating).join(Author).all()
        return render_template("home.html", books=new_books, success=True)
    except Exception as e:  # Catch all exceptions for debugging
        print("AN ERROR HAS OCCURED: ", e)
        return render_template("home.html", books=books, success=False)

@app.route('/search', methods=['POST'])
def search():
    """
    Route to search books by any term (title, author, year) via POST.
    Returns books matching the search term.
    """
    title = request.form['search']
    title = '%' + title + '%'
    books = db.session.query(Book.id, Book.isbn, Book.title,
                             Author.name, Book.author_id, Book.publication_year) \
        .join(Author).filter(Book.title.contains(title)
        | Author.name.contains(title) | Book.publication_year
        .contains(title)).all()
    if len(books) == 0:
        return render_template("home.html", error=True)
    return render_template("home.html", books=books)

@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """
    Route to delete a book by id. Deletes the author if it was their only book.
    """
    if request.method != "POST" or request.form.get("confirmation", "") != "yes":
        if request.method == "POST" and request.form.get("confirmation", "") != "no":
            book = [Book.query.get(book_id)]
            return render_template("home.html", books=book, book_confirmation=book_id)
        books = db.session.query(Book.id, Book.isbn, Book.title,
                                 Author.name, Book.author_id,
                                 Book.publication_year, Book.rating).join(Author).all()
        return render_template("home.html", books=books)
    book = Book.query.get(book_id)
    if book:
        author_id = book.author_id
        db.session.delete(book)
        db.session.commit()
        books_auth = db.session.query(Book.title).filter(Book.author_id == author_id).all()
        if len(books_auth) == 0:
            author = Author.query.get(author_id)
            db.session.delete(author)
            db.session.commit()
        books = db.session.query(Book.id, Book.isbn, Book.title,
                                 Author.name, Book.author_id,
                                 Book.publication_year, Book.rating).join(Author).all()
        return render_template('home.html', books=books, deleted=True)
    else:
        books = db.session.query(Book.id, Book.isbn, Book.title,
                                 Author.name, Book.author_id,
                                 Book.publication_year, Book.rating).join(Author).all()
        return render_template('home.html', books=books, deleted=False)

@app.route('/author/<int:author_id>/delete', methods=['POST'])
def delete_author(author_id):
    """
    Route to delete an author by id.
    """
    if request.method != "POST" or request.form.get("confirmation", "") != "yes":
        if request.method == "POST" and request.form.get("confirmation", "") != "no":
            books = db.session.query(Book).filter(Book.author_id == author_id).all()
            return render_template("home.html", books=books, auth_confirmation=author_id)
        books = db.session.query(Book.id, Book.isbn, Book.title,
                                 Author.name, Book.author_id,
                                 Book.publication_year, Book.rating).join(Author).all()
        return render_template("home.html", books=books)
    author = Author.query.get(author_id)
    if author:
        db.session.delete(author)
        db.session.commit()
        books = db.session.query(Book.id, Book.isbn, Book.title,
                                 Author.name, Book.author_id,
                                 Book.publication_year, Book.rating).join(Author).all()
        return render_template('home.html', books=books, auth_deleted=True)
    else:
        books = db.session.query(Book.id, Book.isbn, Book.title,
                                 Author.name, Book.author_id,
                                 Book.publication_year, Book.rating).join(Author).all()
        return render_template('home.html', books=books, auth_deleted=False)

@app.route('/author/<int:author_id>', methods=['GET'])
def author(author_id):
    """
    Route to display details of an author by id.
    """
    author = Author.query.get(author_id)
    return render_template("details_author.html", author=author)

@app.route('/book/<int:book_id>', methods=['GET'])
def book(book_id):
    """
    Route to display details of a book by id.
    """
    book = db.session.query(Book.isbn, Book.title,
                            Book.publication_year, Author.name, Book.rating) \
        .join(Author).filter(Book.id == book_id).one()._mapping
    return render_template("details_book.html", book=book)

@app.route('/book/rating/<int:book_id>', methods=['POST'])
def rate_book(book_id):
    """
    Route to set rating for a book by id.
    """
    rating = request.form['rating']
    book = Book.query.get(book_id)
    book.rating = rating
    db.session.commit()
    books = db.session.query(Book.id, Book.isbn, Book.title,
                             Author.name, Book.author_id,
                             Book.publication_year, Book.rating).join(Author).all()
    return render_template('home.html', books=books, rated=True)

@app.route("/get_ai_recommendation", methods=["GET"])
def get_ai_recommendation():
    """
    Route to get AI recommendation for books/authors (bonus).
    Calls an external function to get recommendations.
    """
    books = db.session.query(Book.title, Book.publication_year,
                             Author.name, Book.rating).join(Author).all()
    dataset = ""
    for book in books:
        dataset += str(book)
    return render_template("ai_recomendation.html",
                           recomendation=ai_request.ai_request(dataset))

# Start the Flask server
app.run(host="0.0.0.0", port=5002, debug=True)

# Only needed to create tables once (commented out after first use)
# with app.app_context():
#   db.create_all()
