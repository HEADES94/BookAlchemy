# My Online Library 📚

A Flask-based digital library app for managing your books and authors!

## Features

- Add, list, and delete books and authors
- Assign books to authors
- Rate books
- Search, sort, and filter your collection
- Book cover images fetched automatically via ISBN
- Responsive, modern interface

## Tech Stack

- Python 3.x
- Flask
- Flask-SQLAlchemy
- Jinja2
- SQLite

## Setup

1. **Clone the repository**  
   `git clone <your-repo-url>`

2. **Create a virtual environment & install dependencies**  
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

Create folders if missing:
```bash
mkdir -p data instance static templates
```

```bash
python app.py
```

Configuration
The database is stored in /data/library.sqlite

Add your environment variables (e.g., API keys) in .env if needed.

