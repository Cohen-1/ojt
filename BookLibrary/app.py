from datetime import datetime
from flask import Flask, jsonify, request, abort, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__, static_folder="static", static_url_path="")

# In production, set allowed origins to your deployed URL, e.g. https://your-app.onrender.com
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=False,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    max_age=86400,
)

# SQLite file path (Render/Railway can support it if you attach a disk; for serious use, switch to Postgres)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///books.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "title": self.title, "author": self.author}

with app.app_context():
    db.create_all()

@app.get("/books")
def list_books():
    books = Book.query.order_by(Book.id.desc()).all()
    return jsonify([b.to_dict() for b in books])

@app.post("/books")
def create_book():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    author = (data.get("author") or "").strip()
    if not title or not author:
        abort(400, "title and author are required")
    book = Book(title=title, author=author)
    db.session.add(book)
    db.session.commit()
    return jsonify(book.to_dict()), 201

@app.put("/books/<int:book_id>")
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    author = (data.get("author") or "").strip()
    if not title or not author:
        abort(400, "title and author are required")
    book.title = title
    book.author = author
    db.session.commit()
    return jsonify(book.to_dict())

@app.delete("/books/<int:book_id>")
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({"ok": True})

# Serve the web app (static index.html)
@app.route("/")
def root():
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    # For local testing
    app.run(host="0.0.0.0", port=5000, debug=True)
