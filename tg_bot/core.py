import datetime
import json
import time
from operator import and_
from pathlib import Path

from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm.exc import DetachedInstanceError
from sqlalchemy_utils import Choice

from settings import SLEEP_AFTER_INFO, MEDIA_FOLDER, ROOT_DIR
from survey.models import Session, Question, Questionnaire, QuestionTypes
from tg_bot.server import bot, run_polling
from tg_bot.helper import get_markup, DataCheckError, build_callback
from tg_bot.management import get_user, handle_user_edit, handle_toggle_is_admin, handle_toggle_is_interviewer, \
	handle_assign_to_projects, handle_assign_user_to_project, handle_assign_admin_to_project, handle_project_edit, \
	handle_toggle_is_active, handle_assign_users
from utils import get_distance
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
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
	'select_project': handle_project_edit,
	'toggle_is_active': handle_toggle_is_active,
	'assign_users': handle_assign_users,
}


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
	if call.data == 'dummy':
		print('No call data')
		return
	# user = get_user(call)
	# print('call', call)
	# if user.is_admin or user.is_root: #todo: check security
	callback = json.loads(call.data)
	action = callback.get('action')
	args = callback.get('args', [])
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
		'manage_projects': 'Управление моими проектами',
	}
	user = get_user(message)
	if user.is_interviewer:
		cmds.update(**{
			'surveys': 'Показать список доступных опросов',
		})
	if user.is_admin or user.is_root:
		cmds.update(**{
			'users': 'Показать список пользователей',
			'manage_users': 'Управление правами пользователей',
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
# 	if question.type.code == types.info:
# 		time.sleep(SLEEP_AFTER_INFO)
# 		handle_answer(msg, question=question)
# 		return
# 	bot.register_next_step_handler(msg, handle_answer, question=question)

def before_question_ask(question, message):
	print('before_question_ask', question.code)
	if question.code == 'shops':
		shops = [
			{
				'name': 'ГУМ', 'address': 'Красная площадь, 3, Москва, 109012',
				'latitude': 55.7546942, 'longitude': 37.6214334
			},
		]
		s = Session()
		result_table = question.questionnaire.result_table
		latitude, longitude = s.query(result_table.q2_latitude, result_table.q2_longitude).filter(result_table.started_by_id == message.from_user.id).first()
		msg = ''
		distance_tolerance = 5
		for shop in shops:
			shop['distance'] = round(get_distance(latitude, longitude, lat2=shop['latitude'], lon2=shop['longitude']), 1)
			msg += '\t{name}, distance: {distance}km\n'.format(**shop)
		print('before_question_ask', 'question.categories', question.categories)
		question.set_filter(func=lambda cat: shops[int(cat.code) - 1]['distance'] < distance_tolerance)
		print('before_question_ask after filter', 'question.categories', question.categories)
		bot.send_message(message.chat.id, f'All shops are:\n{msg}But only the ones within {distance_tolerance}km will be available for selection.')
		if len(question.categories) == 0:
			closest = sorted(shops, key=lambda a: a['distance'])[0]
			bot.send_message(
				message.chat.id,
				'Ни одного магазина поблизости :( Попробуй подойти ближе и отправить точку еще раз\nЕсли что ближайший в {distance}км от тебя:\n{name}, {address}'.format(
					**closest
				)
			)


def check_data(question, message):
	if question.type.code == QuestionTypes.location and message.content_type != QuestionTypes.location:
		# print('check_data')
		raise DataCheckError('Location error')
	elif question.type.code == QuestionTypes.categorical:
		ok = message.text in [i.text for i in question.categories]
		if not ok:
			raise DataCheckError('Category {} doesn\'t exist'.format(message.text))
	elif question.type.code == QuestionTypes.photo and message.content_type != QuestionTypes.photo:
		raise DataCheckError('Not a photo error')
	elif question.type.code in {QuestionTypes.text, QuestionTypes.integer} and message.content_type != QuestionTypes.text:
		raise DataCheckError('Not a text error')
	elif question.type.code == QuestionTypes.integer:
		if not message.text.isnumeric():
			try:
				float(message.text)
			except ValueError:
				raise DataCheckError('Not a number error')
	print('warning: data check is not handled for ', question.code, question.type)
	return True



def handle_save(question, message): #todo handle all saves to db
	print('handle_save', question.code)
	if not question.save_in_survey:
		return
	check_data(question, message)
	session = Session()
	try:
		response = question.get_response_object(message.from_user.id)
	except (DetachedInstanceError, ProgrammingError):
		question = session.query(Question).filter(Question.id == question.id).first()
		response = question.get_response_object(message.from_user.id)

	if question.type.code == QuestionTypes.categorical:
		code = None
		for cat in question.categories:
			if cat.text == message.text:
				code = cat.id
				break
		response.__setattr__(question.code, code)
		session.add(response)
		session.commit()
	elif question.type.code == QuestionTypes.location:
		response.__setattr__(f'{question.code}_latitude', message.location.latitude)
		response.__setattr__(f'{question.code}_longitude', message.location.longitude)
		session.add(response)
		session.commit()
	elif question.type.code == QuestionTypes.photo:
		file_info = bot.get_file(message.photo[-1].file_id)
		print('handle_save', 'photo', file_info)
		downloaded_file = bot.download_file(file_info.file_path)
		file_name = '{}_{}'.format(message.from_user.id, file_info.file_path.split('/')[-1])
		file_folder = Path(MEDIA_FOLDER, question.questionnaire.results_table_name)
		file_path = Path(file_folder, file_name)
		# file_path.mkdir(parents=True)
		try:
			with open(file_path, 'wb') as out:
				out.write(downloaded_file)
		except FileNotFoundError:
			file_folder.mkdir(parents=True)
			with open(file_path, 'wb') as out:
				out.write(downloaded_file)
		print('handle_save', 'file saved', file_path)
		print('handle_save', 'file saved relative', str(file_path.relative_to(ROOT_DIR)))
		response.__setattr__(question.code, str(file_path.relative_to(ROOT_DIR)))
		session.add(response)
		session.commit()
	elif question.type.code == QuestionTypes.timestamp:
		response.__setattr__(question.code, datetime.datetime.now())
		session.add(response)
		session.commit()
	elif question.type.code == QuestionTypes.text or question.type.code == QuestionTypes.integer:
		print('TEXT Q TYPE', message.content_type, message.content_type == 'text')
		response.__setattr__(question.code, message.text)
		session.add(response)
		session.commit()
	else:
		print('handle_save', 'QUESTION TYPE NOT HANDLED FOR SAVE', question.type)



		# bot.send_message(message.chat.id, f'Ого, ты в {dist}км от центра Москвы!')

	# logger.info(' '.join(('question', repr(question), 'is saved to db with:', str(message.json))))
def handle_datacheck_error(question, message, error, flags):
	if question.code == 'shops' and message.content_type == QuestionTypes.location:
		handle_save(get_previous_question(question), message)
		# msg = bot.send_message(message.chat.id, question.text, reply_markup=get_markup(question), )
		# handle_answer(message, question=get_previous_question(question))
		# bot.register_next_step_handler(message, handle_answer, question=question, flags={Flags.goto_start})
		# if Flags.no_step_register not in flags:
		# 	bot.register_next_step_handler(message, handle_answer, question=question, flags={Flags.no_step_register})
		# return

	else:
		bot.send_message(message.chat.id, error.msg)
	flags.add(Flags.goto_start)
	handle_answer(message, question=question, flags=flags)
	# msg = bot.send_message(message.chat.id, question.text, reply_markup=get_markup(question), )
	# if Flags.previous_question in flags:
	# 	if Flags.no_step_register not in flags:
	# 		print('Flags.previous_question in flags')
	# 		bot.register_next_step_handler(msg, handle_answer, question=get_previous_question(question))
	# else:
	# 	if Flags.no_step_register not in flags:
	# 		bot.register_next_step_handler(msg, handle_answer, question=question)

class Flags:
	goto_start = 'goto_start'
	terminate = 'terminate'
	previous_question = 'previous_question'
	add_back_button = 'back_button'
	no_step_register = 'no_step_register'


def handle_answer(message, *args, **kwargs):
	flags = kwargs.get('flags', set())
	# print('handle_answer', 'kwargs', kwargs)
	# print('handle_answer', 'flags', flags)

	if message.text == '/start':
		handle_start(message)
		flags.add(Flags.terminate)
	if message.text == '/cancel':
		handle_cancel(message)
		flags.add(Flags.terminate)
	if message.text == '/help':
		handle_help(message)

	if Flags.terminate in flags:
		terminate(message)
		return

	question = kwargs.get('question')

	if Flags.goto_start not in flags:
		if not question:
			terminate(message)
		try:
			handle_save(question, message)
		except DataCheckError as e:
			handle_datacheck_error(question, message, e, flags)

			return

		# after_question_ask(question, message)
		bot.send_message(message.chat.id, f'Question: {question.code}, step: {question.step}, END')
		question = get_next_question(question) if Flags.previous_question not in flags else get_previous_question(question)

	if not question:
		terminate(message)
		return

	try:
		bot.send_message(message.chat.id, f'Question: {question.code}, step: {question.step}, START')
	except AttributeError:
		terminate(message)
		return

	# print("Q.RESPONSE", question.code, question.get_response_object(message.from_user.id))

	before_question_ask(question, message)

	if question.type.code in {QuestionTypes.info, QuestionTypes.sticker}:
		msg = bot.send_message(message.chat.id, question.text, reply_markup=get_markup(question), )
		time.sleep(SLEEP_AFTER_INFO)
		handle_answer(msg, question=question)
		return
	if question.type.code == QuestionTypes.timestamp:
		handle_save(question, message)
		handle_answer(message, question=question)
		return

	msg = bot.send_message(message.chat.id, question.text, reply_markup=get_markup(question))
	if Flags.no_step_register not in flags:
		bot.register_next_step_handler(msg, handle_answer, question=question)


def terminate(message):
	bot.send_message(message.chat.id, 'Survey is over')
	return


def get_next_question(question):
	session = Session()
	return session.query(Question).filter(Question.step == question.step + 1).first()

def get_previous_question(question):
	print('Previous question requested for ', question.code)
	session = Session()
	return session.query(Question).filter(Question.step == question.step - 1).first()

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
