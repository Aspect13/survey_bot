import json
import time
from operator import and_

from settings import SLEEP_AFTER_INFO, TMP_FILE
from survey.models import Session, Question, User, QuestionTypes as types, Questionnaire, QuestionTypes
from tg_bot.server import bot, run_polling, logger
from tg_bot.helper import get_markup, DataCheckError, build_callback
from tg_bot.user_management import get_user, handle_user_edit, handle_toggle_is_admin, handle_toggle_is_interviewer, \
	handle_assign_to_projects, handle_assign_user_to_project, handle_assign_admin_to_project
from utils import get_distance
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
	InlineKeyboardButton


def handle_start_survey(call, questionnaire_id):
	print('handle_start_survey', questionnaire_id)
	session = Session()
	name, description = session.query(Questionnaire.name, Questionnaire.description).filter(Questionnaire.id == questionnaire_id).first()
	markup = ReplyKeyboardMarkup(one_time_keyboard=True)
	buttons = (KeyboardButton(text='Да'), KeyboardButton(text='Нет'))
	markup.add(*buttons)
	msg = bot.send_message(call.message.chat.id, f'Начать опрос {name}?\n({description})', reply_markup=markup)
	bot.register_next_step_handler(msg, handle_start_survey_answer, questionnaire_id)


ACTION_RESOLVER = {
	'select_user': handle_user_edit,
	'toggle_is_admin': handle_toggle_is_admin,
	'toggle_is_interviewer': handle_toggle_is_interviewer,
	'assign_to_projects': handle_assign_to_projects,
	'assign_user_to_project': handle_assign_user_to_project,
	'assign_admin_to_project': handle_assign_admin_to_project,
	'start_survey': handle_start_survey,
	'select_project': None,
}


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
	if call.data == 'dummy':
		print('No call data')
		return
	user = get_user(call)
	print('call', call)
	# with open(TMP_FILE, 'w') as out:
	# 	out.write(str(call))

	if user.is_admin or user.is_root:
		callback = json.loads(call.data)
		action = callback.get('action')
		args = callback.get('args', [])
		# if action == 'select_user':
		# 	handle_edit(call, *args)
		# elif action == 'toggle_is_admin':
		# 	handle_toggle_is_admin(call, *args)
		# elif action == 'toggle_is_interviewer':
		# 	handle_toggle_is_interviewer(call, *args)
		# elif action == 'assign_to_projects':
		# 	handle_assign_to_projects(call, *args)
		# elif action == 'assign_user_to_project':
		# 	handle_assign_user_to_project(call, *args)
		# elif action == 'assign_admin_to_project':
		# 	handle_assign_admin_to_project(call, *args)
		# else:
		func = ACTION_RESOLVER.get(action)
		if func:
			func(call, *args)
			return
		print('NO HANDLER FOR ACTION: ', action)
	bot.send_message(call.message.chat.id, 'No actions available')





@bot.message_handler(commands=['help'])
def handle_help(message):
	cmds = {
		'help': 'Показать это сообщение',
		'cancel': 'Прервать и выйти в главное меню',
	}
	user = get_user(message)
	if user.is_interviewer:
		cmds.update(**{
			'surveys': 'Показать список доступных опросов',
		})
	if user.is_admin or user.is_root:
		cmds.update(**{
			'users': 'Показать список пользователей',
			'manage_users': 'Раздать права всякие',
		})
	bot.send_message(message.chat.id, '\n'.join([f'/{k} - {v}' for k, v in cmds.items()]))



@bot.message_handler(commands=['start'])
def handle_start(message):
	bot.send_message(message.chat.id, 'Привет! Я - Polly, бот для проведения опросов!')
	get_user(message)
	handle_help(message)
	return


@bot.message_handler(commands=['cancel'])
def handle_cancel(message):
	bot.send_message(message.chat.id, 'Ok, вернемся в начало.')
	handle_help(message)
	return


@bot.message_handler(commands=['surveys'])
def handle_surveys(message, *args, **kwargs):
	inactive_count = 0
	user = get_user(message)
	markup = InlineKeyboardMarkup()
	for i in user.available_questionnaires:
		if i.is_active:
			btn = InlineKeyboardButton(str(i), callback_data=build_callback('start_survey', i.id))
			markup.add(btn)
		elif user.is_admin or user.is_root:
			inactive_count += 1

	bot.send_message(message.chat.id, f'Доступно {len(user.available_questionnaires) - inactive_count}:\n', reply_markup=markup)
	if inactive_count and (user.is_admin or user.is_root):
		bot.send_message(message.chat.id, f'There are {inactive_count} inactive projects, /manage_projects')






def handle_start_survey_answer(message, questionnaire_id):
	print('handle_start_survey_answer', questionnaire_id)
	if message.text == 'Да':
		session = Session()
		question = session.query(Question).filter(and_(Question.questionnaire_id == questionnaire_id, Question.step == 1)).first()
		handle_answer(message, question=question, flags={Flags.goto_start})
	else:
		handle_cancel(message)



# def start_survey(message, *args, **kwargs):
# 	session = Session()
# 	question = session.query(Question).filter(Question.step == 1).first()
# 	bot.send_message(message.chat.id, f'Question: {question.code}, step: {question.step}, START')
# 	msg = bot.send_message(message.chat.id, question.text, reply_markup=get_markup(question), )
# 	if question.type == types.info:
# 		time.sleep(SLEEP_AFTER_INFO)
# 		handle_answer(msg, question=question)
# 		return
# 	bot.register_next_step_handler(msg, handle_answer, question=question)


def check_data(question, message):
	if question.type == types.location and message.content_type != types.location:
		# print('check_data')
		raise DataCheckError('Location error')
	if question.type == types.categorical:
		ok = message.text in [i.text for i in question.categories]
		# for i in question.categories:
		# 	if i.text == message.text:
		# 		return True
		if not ok:
			raise DataCheckError('Category {} doesn\'t exist'.format(message.text))
	return True


def handle_save(question, message): #todo handle all saves to db
	if not question.save_in_survey:
		return
	check_data(question, message)
	if question.type == types.location:
		latitude, longitude = message.location.latitude, message.location.longitude
		dist = round(get_distance(latitude, longitude), 1)
		bot.send_message(message.chat.id, f'Ого, ты в {dist}км от центра Москвы!')
	# logger.info(' '.join(('question', repr(question), 'is saved to db with:', str(message.json))))


class Flags:
	goto_start = 'goto_start'
	terminate = 'terminate'


def handle_answer(message, *args, **kwargs):
	if message.text == '/start':
		handle_start(message)
	if message.text == '/cancel':
		handle_cancel(message)
	if message.text == '/help':
		handle_help(message)

	flags = kwargs.get('flags', {})
	if Flags.terminate in flags:
		terminate(message)

	question = kwargs.get('question')

	if Flags.goto_start not in flags:
		if not question:
			terminate(message)
		try:
			handle_save(question, message)
		except DataCheckError as e:
			bot.send_message(message.chat.id, e.msg)
			msg = bot.send_message(message.chat.id, question.text, reply_markup=get_markup(question), )
			bot.register_next_step_handler(msg, handle_answer, question=question)
			return

		# after_question_ask(question, message)
		bot.send_message(message.chat.id, f'Question: {question.code}, step: {question.step}, END')
		question = get_next_question(question)

	if not question:
		terminate(message)

	try:
		bot.send_message(message.chat.id, f'Question: {question.code}, step: {question.step}, START')
	except AttributeError:
		terminate(message)

	# before_question_ask(question, message)

	if question.type in {QuestionTypes.info, QuestionTypes.sticker}:
		msg = bot.send_message(message.chat.id, question.text, reply_markup=get_markup(question), )
		time.sleep(SLEEP_AFTER_INFO)
		handle_answer(msg, question=question)
		return

	msg = bot.send_message(message.chat.id, question.text, reply_markup=get_markup(question))
	bot.register_next_step_handler(msg, handle_answer, question=question)


def terminate(message):
	bot.send_message(message.chat.id, 'That is all over')
	return


def get_next_question(question):
	session = Session()
	return session.query(Question).filter(Question.step == question.step + 1).first()


if __name__ == '__main__':
	# # Enable saving next step handlers to file "./.handlers-saves/step.save".
	# # Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
	# # saving will hapen after delay 2 seconds.
	# bot.enable_save_next_step_handlers(delay=2)
	#
	# # Load next_step_handlers from save file (default "./.handlers-saves/step.save")
	# # WARNING It will work only if enable_save_next_step_handlers was called!
	# bot.load_next_step_handlers()
	run_polling()
