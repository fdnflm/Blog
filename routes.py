# Import flask dependencies
from flask import request, render_template, \
      flash, redirect, url_for, abort
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from app import db, moment, app, mail, api
from forms import LoginForm, EditProfile, UploadPhoto, EditPassword, EditPost, RegistrationForm, AddComment
from flask_login import current_user, login_user, logout_user, login_required
from models import User, Post, Comment, Like
from misc import generate_id, check_confirmed, InlineKeyboard, InlineButton
import os
from datetime import datetime, timedelta
from flask_mail import Message
from config import CHANNEL_ID, BASE_DIR


@app.route("/")
@app.route("/<filter_by>")
def home(filter_by=None):
	posts = []
	if filter_by == "today":
		get_posts = Post.query.all()
		for post in get_posts:
			if str(post.date_created)[:10] == str(datetime.utcnow())[:10]:
				posts.append(post)
	elif filter_by == "last_week":
		week_ago = datetime.utcnow() - timedelta(weeks=1)
		posts = Post.query.filter(Post.date_created > week_ago).all()
	elif filter_by == "last_month":
		month_ago = datetime.utcnow() - timedelta(weeks=4)
		posts = Post.query.filter(Post.date_created > month_ago).all()
	elif filter_by is None:
		posts = Post.query.all()
	else:
		abort(404)
	return render_template("blog/index.html",
	                       title="Home",
	                       posts=posts,
	                       reversed=reversed)


@app.route("/post/<post_id>")
def post(post_id):
	post = Post.query.filter_by(id=post_id).first_or_404()
	comments = Comment.query.filter_by(post_id=post_id).all()
	likes = Like.query.filter_by(post_id=post_id).all()
	is_liked = Like.query.filter(Like.user_id == current_user.id).filter(
	    Like.post_id ==
	    post.id).first() if not current_user.is_anonymous else None
	form = AddComment()
	week_ago = datetime.utcnow() - timedelta(weeks=1)
	lw_posts = Post.query.filter(Post.date_created > week_ago).join(
	    Like, Post.likes).all()
	combo = []
	for p in lw_posts:
		combo.append((p, len(p.likes)))
	filtered = reversed(sorted(combo[:3], key=lambda combo: combo[1]))
	return render_template("blog/post.html", title=post.title, post=post, \
                             form=form, comments=comments, total_likes=len(likes), is_liked=is_liked, lw_posts=filtered)


@app.route("/delete_post/<post_id>")
@login_required
def delete_post(post_id):
	post = Post.query.filter_by(id=post_id).first_or_404()
	if current_user.role is 1 and current_user.id == post.author.id:
		if post.img:
			os.remove(os.path.join("static/uploads", post.img))
		current_user.posts_value = current_user.posts_value - 1
		db.session.delete(post)
		db.session.commit()
		return redirect("/")
	else:
		abort(403)
	return redirect("/")


@app.route("/add_comment", methods=["POST"])
@login_required
def add_comment():
	form = AddComment()
	if form.validate_on_submit():
		comment = Comment(form.body.data, request.referrer[-1:],
		                  current_user.id)
		db.session.add(comment)
		db.session.commit()
		return redirect(request.referrer)
	return redirect(request.referrer)


@app.route("/add_like", methods=["POST"])
@login_required
def add_like():
	post = Post.query.get(request.form.get("post_id"))
	if not post:
		abort(404)
	like = Like(post.id, current_user.id)
	user = User.query.get(post.author.id)
	user.likes_value = user.likes_value + 1
	db.session.add(like)
	db.session.commit()
	return "1"


@app.route("/share", methods=["POST"])
def share():
	post = Post.query.get(request.form.get("post_id"))
	if not post:
		abort(404)
	user = User.query.get(post.author.id)
	user.shares = user.shares + 1
	db.session.commit()
	return "1"


@app.route("/delete_comment/<comment_id>")
@login_required
def delete_comment(comment_id):
	if current_user.role == 1:
		comment = Comment.query.filter_by(id=comment_id).first_or_404()
		db.session.delete(comment)
		db.session.commit()
		return redirect(request.referrer)
	else:
		abort(403)
	return redirect("/")


@app.route("/ban/<user_id>")
@login_required
def ban_user(user_id):
	if current_user.role == 1:
		user = User.query.filter_by(id=user_id).first_or_404()
		user.banned = 1
		db.session.commit()
		return redirect(request.referrer)
	else:
		abort(403)
	return abort(403)


@app.route("/unban/<user_id>")
@login_required
def unban_user(user_id):
	if current_user.role == 1:
		user = User.query.filter_by(id=user_id).first_or_404()
		user.banned = 0
		db.session.commit()
		return redirect(request.referrer)
	else:
		abort(403)
	return abort(403)


@app.route("/login", methods=["GET", "POST"])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	login_form = LoginForm()
	if login_form.validate_on_submit():
		user = User.query.filter_by(name=login_form.username.data).first()
		if user and check_password_hash(user.password,
		                                login_form.password.data):
			login_user(user, remember=login_form.remember.data)
			next_page = request.args.get('next')
			if not next_page or url_parse(next_page).netloc != '':
				next_page = url_for('home')
			return redirect(next_page)
		else:
			flash("Неправильный логин или пароль")
			return redirect(url_for('login'))
	return render_template("auth/login.html", title="Sign In", form=login_form)


@app.route("/register", methods=["GET", "POST"])
def register():
	if current_user.is_authenticated:
		return redirect("/")
	form = RegistrationForm()
	if request.method == "POST":
		if form.validate_on_submit():
			user = User(form.username.data,
			            generate_password_hash(form.password.data))
			user.email = form.email.data
			db.session.add(user)
			db.session.commit()
			login_user(user)
			return redirect("/send_confirm")
	return render_template("auth/register.html", form=form, title="Sign Up")


@app.route('/logout')
def logout():
	logout_user()
	return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
@login_required
@check_confirmed
def profile():
	edit_form = EditProfile(current_user.name)
	password_form = EditPassword()
	uplaod_photo = UploadPhoto()

	if uplaod_photo.validate_on_submit():
		avatar = uplaod_photo.photo.data
		filename = secure_filename(generate_id(6) + ".jpg")
		avatar.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
		current_user.avatar_id = filename
		db.session.commit()
		return redirect("/profile")

	if edit_form.validate_on_submit():
		current_user.name = edit_form.username.data
		current_user.bio = edit_form.bio.data
		db.session.commit()
		return redirect("/profile")
	elif request.method == 'GET':
		edit_form.username.data = current_user.name
		edit_form.bio.data = current_user.bio

	if password_form.validate_on_submit():
		if check_password_hash(current_user.password,
		                       password_form.password_old.data):
			current_user.password = generate_password_hash(
			    password_form.password.data)
			db.session.commit()
			return redirect("/profile")

	return render_template("profile.html",
	                       form=edit_form,
	                       upload_ph=uplaod_photo,
	                       password_form=password_form,
	                       title="Profile")


@app.route("/edit_post/<post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
	post = Post.query.filter_by(id=post_id).first_or_404()
	if current_user.role is 1 and current_user.id == post.author.id:
		form = EditPost()
		if request.method == "GET":
			form.title.data = post.title
			form.description.data = post.description
			form.body.data = post.body
			return render_template("blog/edit_post.html", form=form, post=post)
		else:
			post.title = form.title.data
			post.description = form.description.data
			post.body = form.body.data
			picture = form.photo.data
			if picture:
				if post.img:
					os.remove(os.path.join("static/uploads", post.img))
				filename = secure_filename(generate_id(12) + ".jpg")
				picture.save(os.path.join("static/uploads/", filename))
				post.img = filename
			db.session.commit()
			return redirect("/")
	else:
		abort(403)
	return render_template("blog/edit_post.html", form=form, title="Edit Post")


@app.route("/new_post", methods=["GET", "POST"])
@login_required
def new_post():
	if current_user.role is 1:
		form = EditPost()
		if request.method == "POST":
			if form.validate_on_submit():
				picture = form.photo.data
				post = Post(form.title.data, form.description.data,
				            form.body.data, current_user.id)
				# markup = InlineKeyboard()
				# link = InlineButton(
				#     "Читать в блоге",
				#     request.url_root + f"post/{len(Post.query.all()) + 1}")
				# markup.add(link)
				if picture:
					filename = secure_filename(generate_id(12) + ".jpg")
					picture.save(os.path.join("static/uploads/", filename))
					post.img = filename
				# 	api.send_photo(
				# 		CHANNEL_ID,
				# 		open(BASE_DIR + f"\\static\\uploads\\{filename}",
				# 				"rb"),
				# 		f"*{post.title}*\n\n{post.description}",
				# 		reply_markup=markup)
				# else:
				# 	api.send_message(
				# 		CHANNEL_ID,
				# 		f"*{post.title}*\n\n{post.description}",
				# 		reply_markup=markup)
				current_user.posts_value = current_user.posts_value + 1
				db.session.add(post)
				db.session.commit()
				return redirect("/")
	else:
		abort(403)
	return render_template("blog/new_post.html",
	                       form=form,
	                       title="Create a new post")


@app.route("/user/<username>")
@check_confirmed
def user(username):
	user = User.query.filter_by(name=username).first_or_404()
	return render_template("blog/user.html",
	                       user=user,
	                       posts=Post.query.filter_by(user_id=user.id).all(),
	                       reversed=reversed,
	                       title=user.name)


@app.errorhandler(404)
def not_found(error):
	return render_template('404.html'), 404


@app.errorhandler(403)
def forbidden(error):
	return render_template('403.html'), 403


@app.route("/send_confirm")
@login_required
def send_mail():
	msg = Message("Подтвердите ваш аккаунт.",
	              recipients=[current_user.email],
	              sender=app.config["MAIL_DEFAULT_SENDER"])
	token = generate_id(32)
	link = request.url_root + f"confirm/{token}"
	current_user.confirm_token = token
	db.session.commit()
	msg.body = f"Привет, {current_user.name}!\nВы недавно зарегистрировались в нашем блоге! Чтобы активировать аккаунт, перейдите по ссылке ниже\n{link}"
	mail.send(msg)
	return redirect("/unconfirmed")


@app.route("/confirm/<token>")
@login_required
def confirm(token):
	user = User.query.filter_by(confirm_token=token).first_or_404()
	user.confirmed = 1
	user.confirm_token = "confirmed"
	db.session.commit()
	return redirect("/")


@app.route("/unconfirmed")
@login_required
def unconfirmed():
	if current_user.confirmed:
		return redirect("/")
	return render_template("unconfirmed.html")


@app.route("/telegram_api", methods=["POST"])
def telegram_api():
	print(request.json)
	return {"ok": True}


@app.before_request
def before_app_request():
	if current_user.is_authenticated and current_user.banned is 1:
		return render_template("banned.html")
	# if request.MOBILE:
	# 	return render_template("mobile.html")

app.register_error_handler(404, not_found)
app.register_error_handler(403, forbidden)
