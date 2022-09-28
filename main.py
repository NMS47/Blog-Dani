import flask_login
from flask import Flask, render_template, redirect, url_for, flash, request, g
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, AnonymousUserMixin, login_user, LoginManager, login_required, current_user, \
    logout_user
from forms import CreatePostForm, ContactForm
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length
from flask_gravatar import Gravatar
from functools import wraps
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import smtplib
import os

Base = declarative_base()

app = Flask(__name__)
# app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)
##GRAVATAR
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dani-blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CONFIGURE TABLES
class Users(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    posts = relationship("BlogPost", back_populates="author")
    date = db.Column(db.String(250), nullable=False)
    # This line is for multiple users, if you want to upgrade the blog in the future. Currently is just for
    # admin to post content
    # comments = relationship("Comment", back_populates="comment_author")


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, ForeignKey('users.id'))
    author = relationship('Users', back_populates='posts')
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    category = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    comments = relationship('Comment', back_populates="parent_post")

## TABLE FOR COMMENTS
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    # FOR MULTIUSERS
    # author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # comment_author = relationship("Users", back_populates="comments")
    author = db.Column(db.String(50), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")
    date = db.Column(db.String(20), nullable=False)
    text = db.Column(db.Text, nullable=False)


db.create_all()


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])

    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(6)])
    submit = SubmitField('Register Now')


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(6)])
    submit = SubmitField('Log In')


class AnonymousUser(AnonymousUserMixin):
    id = None  # add an id attribute to the default AnonymousUser


class CommentForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    comment = CKEditorField("Your comment")
    submit = SubmitField('Post Comment')


## For Loggin In
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.anonymous_user = AnonymousUser


# This is a decorator to protect URL paths that only the admin should enter.
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function

#This function sends email from contact page
def send_email(name: str, email: str, phone, message: str):
    """Takes the contact form information and sends an email"""
    email_1 = "mantecasalvadores@yahoo.com"
    password_1 = 'eoufscvxmavcrcfm'
    email_2 = 'nicolas.salvadores93@gmail.com'
    with smtplib.SMTP('smtp.mail.yahoo.com', 587) as connect_1:
        connect_1.starttls()
        connect_1.login(user=email_1, password=password_1)
        connect_1.sendmail(from_addr=email_1,
                           to_addrs=email_2,
                           msg=f"Subject:Message from {name}\n\n{message}\n\nCel: {phone}\nEmail: {email}")

## For Login
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = Users(
            username=request.form.get("username"),
            email=request.form.get("email"),
            password=generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8),
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash("Successfuly Registered")
        return redirect(url_for('get_all_posts'))
    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        username = Users.query.filter_by(email=request.form.get('email')).first()
        if username:
            if check_password_hash(username.password, request.form.get('password')):
                login_user(username)
                flash("Succesfully logged in")
                return redirect(url_for('get_all_posts'))
            error = "Wrong password, try again"
            return render_template("login.html", error=error, form=form)
        error = "The email doesn't exist, please try again"
    return render_template("login.html", error=error, form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment(
            text=form.comment.data,
            author=form.name.data,
            parent_post=requested_post,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('show_post', post_id=requested_post.id))
    return render_template("post.html", post=requested_post, user=current_user.id, form=form)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        form_data = request.form
        send_email(form_data['name'], form_data['email'], form_data['phone'], form_data['message'])
        return render_template('contact.html', title='Successfully sent your message',
                               subtitle='I will get back to you ASAP', form=form)
    return render_template("contact.html", title=False, form=form)

@app.route("/viajes")
def viajes():
    posts_viajes = BlogPost.query.filter_by(category='Viajes').all()
    print(posts_viajes)
    return render_template("viajes.html", posts=posts_viajes)

@app.route("/montanismo")
def montanismo():
    posts_montanismo = BlogPost.query.filter_by(category='Montañismo').all()
    return render_template("montanismo.html", posts=posts_montanismo)

@app.route("/escalada")
def escalada():
    posts_escalada = BlogPost.query.filter_by(category='Escalada').all()
    return render_template("escalada.html", posts=posts_escalada)

@app.route("/new-post", methods=("GET", "POST"))
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            category=form.category.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, logged_in=current_user.is_authenticated)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        category=post.category,
        img_url=post.img_url,
        body=post.body,
        date=date.today().strftime("%B %d, %Y")
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.category = edit_form.category.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form, logged_in=current_user.is_authenticated)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run()
