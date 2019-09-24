import json

from telebot.types import ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup

from survey.models import QuestionTypes




def build_callback(action, *args):
	d = dict()
	d['action'] = action
	d['args'] = args
	# d['kwargs'] = kwargs
	return json.dumps(d)


def get_markup(question):
	# if q.type == info or q.type == photo:
	# 	return ReplyKeyboardRemove()
	if question.type == QuestionTypes.location:
		markup = ReplyKeyboardMarkup()
		buttons = KeyboardButton(text=question.categories[0].text, request_location=True)
		markup.add(buttons)
		return markup
	if question.type == QuestionTypes.categorical:
		markup = ReplyKeyboardMarkup(one_time_keyboard=True)
		# buttons = (KeyboardButton(text=i.text) for i in question.categories)
		# markup.add(*buttons)
		for i in question.categories:
			markup.add(KeyboardButton(text=i.text))
		return markup
	return ReplyKeyboardRemove()


class DataCheckError(Exception):
	def __init__(self, *args):
		self.msg = 'Wrong data provided'
		if not args:
			args += (self.msg, )
		else:
			self.msg = args[0]
		super().__init__(self, *args)