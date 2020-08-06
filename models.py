from app import db
from flask_login import UserMixin
from app import login_manager
from werkzeug.security import generate_password_hash


# Define a base model for other database tables to inherit
class Base(db.Model):

	__abstract__ = True

	id = db.Column(db.Integer, primary_key=True)
	date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
	date_modified = db.Column(db.DateTime,
	                          default=db.func.current_timestamp(),
	                          onupdate=db.func.current_timestamp())


# Define a User model
class User(UserMixin, Base):
	__tablename__ = 'user'
	name = db.Column(db.String(32), unique=True, index=True)
	email = db.Column(db.String(64), unique=True, index=True)
	password = db.Column(db.String(128))
	avatar_id = db.Column(db.String(32), default="def.png")
	bio = db.Column(db.String(140))
	likes_value = db.Column(db.Integer(), default=0)
	shares = db.Column(db.Integer(), default=0)
	posts_value = db.Column(db.Integer(), default=0)
	role = db.Column(db.Integer(), nullable=False, default=0)
	confirmed = db.Column(db.Integer(), nullable=False, default=0)
	confirm_token = db.Column(db.String(32))
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	comments = db.relationship('Comment', backref='author', lazy=True)
	likes = db.relationship('Like', backref='author', lazy=True)

	def __init__(self, name, password, role=None):
		self.name = name
		self.password = password
		self.role = role

	def __repr__(self):
		return f"<User {self.name}>"


class Post(Base):
	img = db.Column(db.String(12))
	title = db.Column(db.String(32))
	description = db.Column(db.String(140))
	body = db.Column(db.String())
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	comments = db.relationship('Comment',
	                           backref='article',
	                           lazy=True,
	                           cascade="all, delete-orphan")
	likes = db.relationship('Like',
	                        backref='article',
	                        lazy=True,
	                        cascade="all, delete-orphan")

	def __init__(self, title, description, body, user_id, img=None):
		self.title = title
		self.description = description
		self.body = body
		self.user_id = user_id
		self.img = img

	def __repr__(self):
		return '<Post {}>'.format(self.title)


class Comment(Base):
	body = db.Column(db.String(140), nullable=False)
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	reply_id = db.Column(db.Integer, db.ForeignKey('comment.id'))

	def __init__(self, body, post_id, user_id, reply_id=None):
		self.body = body
		self.post_id = post_id
		self.user_id = user_id
		self.reply_id = reply_id


class Like(Base):
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __init__(self, post_id, user_id):
		self.post_id = post_id
		self.user_id = user_id


@login_manager.user_loader
def load_user(id):
	return User.query.get(int(id))


def init_db():
	db.create_all()

	# Create a test user
	new_user = User("admin", generate_password_hash("password"), role=1)
	new_user.confirmed = 1
	db.session.add(new_user)
	db.session.commit()


if __name__ == '__main__':
	init_db()
