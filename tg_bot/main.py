import time
from functools import wraps

from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from settings import TMP_FILE
from survey.gluten_shops.settings import questionnaire
from survey.models import Session, Questionnaire, info, Route, Question, location, categorical, photo, Category
from tg_bot.core import bot, run_polling, logger
from utils import get_distance


def get_markup(q):
	# if q.type == info or q.type == photo:
	# 	return ReplyKeyboardRemove()
	if q.type == location:
		markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
		buttons = types.KeyboardButton(text=q.categories[0].text, request_location=True)
		markup.add(buttons)
		return markup
	if q.type == categorical:
		print('q', q)
		print('q', q.categories)
		markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
		buttons = (types.KeyboardButton(text=i.text) for i in q.categories)
		markup.add(*buttons)
		return markup
	return ReplyKeyboardRemove()


@bot.message_handler(commands=['start'])
def handle_start(message, *args, **kwargs):
	session = Session()
	question = session.query(Question).join(Route).filter(Route.step == 1).first() #todo change to step = 1
	bot.send_message(message.chat.id, f'Question: {question.code}, step: {question.route_step.step}, START')
	msg = bot.send_message(message.chat.id, question.text, reply_markup=get_markup(question), )
	if question.type == info:
		time.sleep(3)
		handle_answer(msg, question=question)
		return
	bot.register_next_step_handler(msg, handle_answer, question=question)


class DataCheckError(Exception):
	def __init__(self, *args):
		self.msg = 'Wrong data provided'
		if not args:
			args += (self.msg, )
		else:
			self.msg = args[0]
		super().__init__(self, *args)


def check_data(question, message):
	if question.type == location and message.content_type != location:
		print('check_data')
		raise DataCheckError('Location error')
	if question.type == categorical:
		for i in question.categories:
			if i.text == message.text:
				return True
		raise DataCheckError('Category doesn\'t exist error')
	return True


def handle_save(question, message): #todo hadle all saves to db
	check_data(question, message)
	if question.type == location:
		latitude, longitude = message.location.latitude, message.location.longitude
		dist = round(get_distance(latitude, longitude), 1)
		bot.send_message(message.chat.id, f'Ого, ты в {dist}км от центра Москвы!')
	logger.info(' '.join(('question', repr(question), 'is saved to db with:', str(message.json))))


def handle_answer(message, *args, **kwargs):
	question = kwargs.get('question')
	if message.text == '/start':
		handle_start(message)
		return

	if not question:
		bot.send_message(message.chat.id, 'That is all over')
		return

	try:
		handle_save(question, message)
	except DataCheckError as e:
		print('DATA ERRROR')
		bot.send_message(message.chat.id, e.msg)
		msg = bot.send_message(message.chat.id, question.text, reply_markup=get_markup(question), )
		bot.register_next_step_handler(msg, handle_answer, question=question)
		return

	bot.send_message(message.chat.id, f'Question: {question.code}, step: {question.route_step.step}, END')

	session = Session()
	question = session.query(Question).join(Route).filter(Route.step == question.route_step.step + 1).first()

	if not question:
		bot.send_message(message.chat.id, 'That is all over')
		return

	bot.send_message(message.chat.id, f'Question: {question.code}, step: {question.route_step.step}, START')

	if question.type == info:
		msg = bot.send_message(message.chat.id, question.text, reply_markup=get_markup(question), )
		time.sleep(3)
		handle_answer(msg, question=question)
		return

	msg = bot.send_message(message.chat.id, question.text, reply_markup=get_markup(question))
	bot.register_next_step_handler(msg, handle_answer, question=question)








# markup_yes_no = ReplyKeyboardMarkup()
# btn_yes = KeyboardButton('Да')
# btn_no = KeyboardButton('Нет')
# markup_yes_no.add(btn_yes, btn_no)
#
#
#
# @bot.message_handler(content_types=['text'])
# def printer(message):
# 	print(message.text)
# 	print(message)
#
#
#
# @bot.message_handler(commands=['start'])
# def handle_q1(message):
# 	msg = bot.send_message(message.chat.id, 'q1', reply_markup=markup_yes_no,)
# 	bot.register_next_step_handler(msg, handle_q2)
#
#
# def handle_q2(message, clear_markup=True):
# 	print(message)
# 	with open(TMP_FILE, 'w') as out:
# 		out.write(str(message))
# 	# json.dump(str(message).replace("'", '"'), )
# 	msg = bot.send_message(message.chat.id, 'q2')
# 	# bot.register_next_step_handler(msg, handle_q1)
#
#
# tmp_d = {'q1': handle_q1, 'q2': handle_q2}
#
# # key_lst = list(tmp_d.keys())
# # this_q_index = key_lst.index(call.message.text)
# # next_q_name = key_lst[this_q_index + 1]
# # tmp_d[next_q_name](call.message)
#






if __name__ == '__main__':


	# Enable saving next step handlers to file "./.handlers-saves/step.save".
	# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
	# saving will hapen after delay 2 seconds.
	bot.enable_save_next_step_handlers(delay=2)

	# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
	# WARNING It will work only if enable_save_next_step_handlers was called!
	bot.load_next_step_handlers()
	run_polling()

