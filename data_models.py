from flask_sqlalchemy import SQLAlchemy

# Create a SQLAlchemy database instance
db = SQLAlchemy()

class Author(db.Model):
    """
    Author model representing a book author.

    Attributes:
        id (int): Primary key, auto-incrementing.
        name (str): Name of the author.
        birth_date (date): Date of birth.
        date_of_death (date): Date of death.
        books (relationship): List of books by the author (one-to-many).
    """
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    birth_date = db.Column(db.Date)
    date_of_death = db.Column(db.Date)

    # Relationship to Book
    books = db.relationship(
        'Book',
        back_populates='author',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    def __str__(self):
        """Return a readable string representation of the Author."""
        output = f'Name: {self.name}, Birth Date: {self.birth_date}'
        return output

class Book(db.Model):
    """
    Book model representing a book.

    Attributes:
        id (int): Primary key, auto-incrementing.
        isbn (str): ISBN number (unique).
        title (str): Title of the book.
        publication_year (int): Year of publication.
        author_id (int): Foreign key referencing Author.
        rating (float): Book rating.
        author (relationship): The author object (many-to-one).
    """
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(13), unique=True)
    title = db.Column(db.String(100))
    publication_year = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Float, default=0.0)

    # Relationship to Author
    author = db.relationship('Author', back_populates='books')

    def __str__(self):
        """Return a readable string representation of the Book."""
        output = f'Title: {self.title}, Year: {self.publication_year}'
        return output
