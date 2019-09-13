import time

from survey.models import Session, info, Route, Question, location, categorical
from tg_bot.utils import bot, run_polling, logger, get_markup, DataCheckError
from utils import get_distance


@bot.message_handler(commands=['start'])
def handle_start(message, *args, **kwargs):
	session = Session()
	question = session.query(Question).join(Route).filter(Route.step == 1).first()  # todo change to step = 1
	bot.send_message(message.chat.id, f'Question: {question.code}, step: {question.route_step.step}, START')
	msg = bot.send_message(message.chat.id, question.text, reply_markup=get_markup(question), )
	if question.type == info:
		time.sleep(3)
		handle_answer(msg, question=question)
		return
	bot.register_next_step_handler(msg, handle_answer, question=question)


def check_data(question, message):
	if question.type == location and message.content_type != location:
		# print('check_data')
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
	# logger.info(' '.join(('question', repr(question), 'is saved to db with:', str(message.json))))


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


if __name__ == '__main__':
	# Enable saving next step handlers to file "./.handlers-saves/step.save".
	# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
	# saving will hapen after delay 2 seconds.
	bot.enable_save_next_step_handlers(delay=2)

	# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
	# WARNING It will work only if enable_save_next_step_handlers was called!
	bot.load_next_step_handlers()
	run_polling()
