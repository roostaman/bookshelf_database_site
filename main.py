from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, Float, String

'''
On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt
'''

app = Flask(__name__)


class Base(DeclarativeBase):
    pass


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
# initialize the app with the extension
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f"<Book {self.title}>"


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    all_books = list(db.session.execute(db.select(Book)).scalars())
    return render_template("index.html", all_books=all_books)


@app.route("/add", methods=["POST", "GET"])
def add():
    if request.method == "POST":
        name = request.form["name"]
        author = request.form["author"]
        rating = request.form["rating"]

        new_book = Book(
            title=name,
            author=author,
            rating=rating
        )
        db.session.add(new_book)
        db.session.commit()

        return redirect(url_for("home"))
    return render_template("add.html")


@app.route("/edit/<int:book_id>", methods=["POST", "GET"])
def edit(book_id):
    book_to_update = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
    if not book_to_update:
        return redirect(url_for("home"))

    if request.method == "POST":
        book_to_update.rating = request.form["rating"]
        db.session.commit()
        return redirect(url_for("home"))

    return render_template("edit.html", book=book_to_update)


@app.route("/delete_book/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    book_to_delete = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
    # book_to_delete = db.get_or_404(Book, book_id)
    db.session.delete(book_to_delete)
    db.session.commit()

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
