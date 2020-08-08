import string
import random
from flask import redirect
from flask_login import current_user
from functools import wraps
from config import BASE_DIR
import requests
import json


def generate_id(length):
	return "".join(random.choice(string.ascii_letters) for i in range(length))


def check_confirmed(func):
	@wraps(func)
	def wrap(*args, **kwargs):
		if current_user.is_anonymous:
			return redirect("/login")
		if current_user.confirmed == 0:
			return redirect("/unconfirmed")
		return func(*args, **kwargs)

	return wrap


class Telegram_API:
	def __init__(self, token):
		self.token = token

	def set_webhook(self):
		req = requests.post(
		    f"https://api.telegram.org/bot{self.token}/setWebhook",
		    data={"url": ""})
		print(req.text, req.status_code)

	def send_message(self, chat_id, message_text, reply_markup=None):
		method = "sendMessage"
		url = f"https://api.telegram.org/bot{self.token}/{method}"
		data = {
		    "chat_id": chat_id,
		    "text": message_text,
		    "parse_mode": "markdown",
		    "reply_markup": json.dumps({'inline_keyboard': reply_markup.get_markup()})
		    if reply_markup else None
		}
		return requests.post(url, data=data)

	def send_photo(self, chat_id, photo, caption=None, reply_markup=None):
		method = "sendPhoto"
		url = f"https://api.telegram.org/bot{self.token}/{method}"
		data = {
		    "chat_id": chat_id,
		    "caption": caption,
		    "parse_mode": "markdown",
		    "reply_markup": json.dumps({'inline_keyboard': reply_markup.get_markup()})
		    if reply_markup else None
		}
		return requests.post(url, data=data, files={"photo": photo})


class InlineKeyboard:
	def __init__(self):
		self.__markup = []

	def add(self, instance):
		if isinstance(instance, InlineButton):
			self.__markup.append([{
			    "text": instance.text,
			    "url": instance.url
			}])

	def add_all(self, *args):
		for item in args:
			if isinstance(item):
				self.__markup.append([{"text": item.text, "url": item.url}])

	def remove(self, index):
		self.__markup.pop(index)

	def clear(self):
		self.__markup.clear()

	def get_markup(self):
		return self.__markup

	def __repr__(self):
		return repr(self.__markup)


class InlineButton:
	def __init__(self, text, url):
		self.text = text
		self.url = url
