"""
Uzduotys:
1.(3) Surasti, isvardinti ir pataisyti visas projekte rastas klaidas zemiau, uz bent 5 rastas ir pataisytas pilnas balas:
    a) User lentelės stulpeliui 'first name' priskirtas tipas Integer. Reikia keisti į String.
    b) def show kintamajam priskirta ne pilna lentelės užklausa, turi būti MyTable.query.all()
    c) def sign_in dekoratoriuje nenurodyti metodai, reikia pridėti methods=['GET', 'POST']
    d) def account_information_update netinkamai nurodyta, kuo užpildyti laukus, visur bus rodomas el.paštas.
    e) def sign_out neįtraukta komanda logout_user().
    f) formoje SignUpForm, def sign_up ir puslapyje sign_up trūksta laukelio last_name.
    g) def sign_up filtruojama pagal email_adress, bet priskiriama laukeliui first name.
    h) def log_out nebuvo logout_user, kuri taip pat reikejo irasyti ir prie import
    ...
2.(7) Praplesti aplikacija ir bibliotekos resgistra pagal apacioje surasytus reikalavimus:
    a)(1) Naudojant SQLAlchemy klases, aprasyti lenteles Book, Author su pasirinktinais atributais su tinkamu rysiu -
        vienas autorius, gali buti parases daug knygu, ir uzregistruoti juos admin'e
    b)(2) Sukurti (papildomus) reikiamus rysius tarp duombaziniu lenteliu, kad atitiktu zemiau pateiktus reikalavimus
    c) Sukurti puslapius Available Books ir My Books:
        i)(2) Available Books puslapis
            - isvesti bent knygos pavadinima ir autoriu
            - turi buti prieinamas tik vartotojui prisijungus,
            - rodyti visas knygas, kurios nera pasiskolintos
            - tureti mygtuka ar nuoroda "Borrow" prie kiekvienos knygos, kuri/ia paspaudus, knyga yra priskiriama
              varototojui ir puslapis perkraunamas
              (del paprastumo, sakome kad kiekvienos i sistema suvestos knygos turima lygiai 1)
        ii)(2) My Books puslapis
            - turi matytis ir buti prieinamas tik vartotojui prisijungus
            - rodyti visas knygas, kurios yra pasiskolintos prisijungusio vartotojo
            - salia kiekvienos knygos mygtuka/nuoroda "Return", kuri/ia paspaudus, knyga grazinama i biblioteka ir
              perkraunamas puslapis
    f)(2) Bonus: praplesti aplikacija taip, kad bibliotekoje kiekvienos knygos galetu buti
        daugiau negu vienas egzempliorius
Pastabos:
    - uzstrigus su pirmaja uzduotimi, galima paimti musu paskutini flask projekto template
        ir ten atlikti antra uzduoti
    - nereikalingus templates geriau panaikinti ar persidaryti, kaip reikia. Tas pats galioja su MyTable klase
    - antram vartotojui prisijungus, nebeturi matytis kyngos, kurios buvo pasiskolintos pirmojo vartotojo
        nei prie Available Books, nei prie My Books
    - visam administravimui, pvz. knygu suvedidimui galima naudoti admin
    - sprendziant bonus uzduoti, apsvarstyti papildomos lenteles isivedima
"""
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_bcrypt import Bcrypt
from flask_login import AnonymousUserMixin, UserMixin, LoginManager, login_user, logout_user, current_user, \
    login_required
from flask_sqlalchemy import SQLAlchemy
import forms

app = Flask(__name__)


class MyAnonymousUserMixin(AnonymousUserMixin):
    is_admin = True


login_manager = LoginManager(app)


login_manager.login_view = 'sign_in'
login_manager.login_message = 'Please login to access this page.'
login_manager.login_message_category = 'info'
login_manager.anonymous_user = MyAnonymousUserMixin

admin = Admin(app)

bcrypt = Bcrypt(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '(/("ZOHDAJK)()kafau029)ÖÄ:ÄÖ:"OI§)"Z$()&"()!§(=")/$'

db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email_address = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    books = db.relationship('Book', back_populates="user")

    def __init__(self, first_name, last_name, email_address, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email_address = email_address
        self.password = password

    def __repr__(self):
        return f'{self.first_name} {self.last_name}'


class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    author = db.relationship('Author', back_populates="books")
    available = db.Column(db.Boolean, nullable=False, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', back_populates="books")

    def __init__(self, author, title, user):
        self.author = author
        self.title = title
        self.user = user

    def __repr__(self):
        return f'{self.title}'


class Author(db.Model):
    __tablename__ = 'author'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    books = db.relationship('Book', back_populates="author")

    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    def __repr__(self):
        return f'{self.first_name} {self.last_name}'


db.create_all()


class MyModelView(ModelView):

    def is_accessible(self):
        return current_user.is_admin


admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Book, db.session))
admin.add_view(MyModelView(Author, db.session))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/available_books')
def available_books():
    data = Book.query.filter(Book.available).all()
    return render_template('available_books.html', data=data)


@app.route('/my_books')
@login_required
def my_books():
    data = Book.query.filter_by(user=current_user).all()
    return render_template('my_books.html', data=data)


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = forms.SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password1.data).decode()
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email_address=form.email_address.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'Welcome, {current_user.first_name}', 'success')
        return redirect(url_for('home'))
    return render_template('sign_up.html', form=form)


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    form = forms.SignInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.email_address.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f'Welcome, {current_user.first_name}', 'success')
            return redirect(request.args.get('next') or url_for('home'))
        flash(f'User or password does not match', 'danger')
        return render_template('sign_in.html', form=form)
    return render_template('sign_in.html', form=form)


@app.route('/borrow_book/<int:id>', methods=['GET', 'POST'])
@login_required
def borrow_book(id):
    book = Book.query.filter_by(id=id).first()
    book.user = current_user
    book.available = False
    db.session.commit()
    flash('Book borrowed successfully', 'success')
    return redirect(url_for('available_books'))


@app.route('/return_book/<int:id>', methods=['GET', 'POST'])
def return_book(id):
    book = Book.query.filter_by(id=id).first()
    book.available = True
    book.user = None
    db.session.commit()
    flash('Book returned successfully', 'success')
    return redirect(url_for('my_books'))


@app.route('/sign_out')
def sign_out():
    logout_user()
    flash('Goodbye, see you next time', 'success')
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
