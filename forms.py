from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email
from flask_wtf.file import FileField, FileRequired, FileAllowed, FileSize
from werkzeug.utils import secure_filename
from models import User


class LoginForm(FlaskForm):
	username = StringField('Имя пользователя', validators=[DataRequired()])
	password = PasswordField('Пароль', validators=[DataRequired()])
	remember = BooleanField('Запомнить меня')
	submit = SubmitField('Вход')


class RegistrationForm(FlaskForm):
	email = StringField("Почта",
	                    validators=[
	                        DataRequired(),
	                        Email(message="Заполните email правильно")
	                    ])
	username = StringField(
	    'Имя пользователя',
	    validators=[
	        DataRequired(),
	        Length(min=5,
	               max=32,
	               message="Минимальная длина - 5, Максимальная - 32")
	    ])
	password = PasswordField('Пароль', validators=[DataRequired()])
	password_repeat = PasswordField('Повторите пароль',
	                                validators=[
	                                    DataRequired(),
	                                    EqualTo(
	                                        "password",
	                                        message="Пароли должны совпадать.")
	                                ])
	submit = SubmitField('Вход')


class UploadPhoto(FlaskForm):
	photo = FileField('image',
	                  validators=[
	                      FileRequired(),
	                      FileAllowed(['jpg', 'jpeg', 'png'],
	                                  'Только фотографии')
	                  ],
	                  id="profile_image")
	submit = SubmitField('Применить', id="apply-btn")


class EditProfile(FlaskForm):
	username = StringField(
	    'Имя пользователя',
	    validators=[
	        DataRequired(),
	        Length(min=5,
	               max=32,
	               message="Минимальная длина - 5, Максимальная - 32")
	    ])
	bio = TextAreaField('Описание',
	                    validators=[
	                        Length(max=140,
	                               message="Максимальная длина 140 символов.")
	                    ])
	submit = SubmitField('Сохранить')

	def __init__(self, original_username, *args, **kwargs):
		super(EditProfile, self).__init__(*args, **kwargs)
		self.original_username = original_username

	def validate_username(self, given_name):
		if given_name.data == self.original_username:
			return True
		else:
			user = User.query.filter_by(name=given_name.data).first()
			if user is not None:
				raise ValidationError('Используйте другое имя')


class EditPassword(FlaskForm):
	password = PasswordField('Новый пароль', validators=[DataRequired()])
	password_old = PasswordField('Старый пароль', validators=[DataRequired()])
	submit = SubmitField('Сохранить')


class EditPost(FlaskForm):
	title = StringField('Заголовок', validators=[DataRequired()])
	description = StringField('Описание', validators=[DataRequired()])
	body = TextAreaField('Текст', validators=[DataRequired()])
	photo = FileField('image',
	                  validators=[
	                      FileAllowed(['jpg', 'jpeg', 'png'],
	                                  'Только фотографии'),
	                      FileSize(max_size=12582912,
	                               message="Максимальный размер файла - 12 мб")
	                  ],
	                  id="image")
	submit = SubmitField('Отправить')


class AddComment(FlaskForm):
	body = TextAreaField("Комментарий",
	                     validators=[
	                         DataRequired(),
	                         Length(max=140,
	                                message="Максимальная длина 140 символов.")
	                     ])
	submit = SubmitField("Опубликовать")
