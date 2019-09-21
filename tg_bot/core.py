import json
import time

from settings import SLEEP_AFTER_INFO, TMP_FILE
from survey.models import Session, Question, User, QuestionTypes as types, Questionnaire
from tg_bot.tg_bot_utils import bot, run_polling, logger
from utils import get_distance
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
	InlineKeyboardButton


def get_markup(question):
	# if q.type == info or q.type == photo:
	# 	return ReplyKeyboardRemove()
	if question.type == types.location:
		markup = ReplyKeyboardMarkup(one_time_keyboard=True)
		buttons = KeyboardButton(text=question.categories[0].text, request_location=True)
		markup.add(buttons)
		return markup
	if question.type == types.categorical:
		markup = ReplyKeyboardMarkup(one_time_keyboard=True)
		buttons = (KeyboardButton(text=i.text) for i in question.categories)
		markup.add(*buttons)
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


def warn_admins(text, session=None):
	if not session:
		session = Session()
	admins = session.query(User).filter(User.is_admin).all()
	for user in admins:
		# bot.send_message(user.chat_id, text)
		bot.send_message(user.tg_id, text)


def create_user(message, session=None):
	if not session:
		session = Session()
	user = User(
		tg_id=message.from_user.id,
		first_name=message.from_user.first_name,
		last_name=message.from_user.last_name,
		# chat_id=message.chat.id,
		username=message.from_user.username,
	)
	user.is_admin = user.tg_id in User.ADMIN_IDS
	session.add(user)
	session.commit()
	print('NEW USER ', user)
	print('NEW USER id', user.id)
	warn_admins('New user joined: {}'.format(repr(user)), session)
	return user


def get_user(message, session=None):
	if not session:
		session = Session()
	user = session.query(User).filter(User.tg_id == message.from_user.id).first()
	if not user:
		user = create_user(message, session)
	return user


def build_callback(action, *args):
	d = dict()
	d['action'] = action
	d['args'] = args
	# d['kwargs'] = kwargs
	return json.dumps(d)


@bot.message_handler(commands=['manage'])
def handle_manage(message):
	user = get_user(message)
	if user.is_admin or user.is_root:
		markup = InlineKeyboardMarkup()
		session = Session()
		users = session.query(User).all()
		# u_list = '\n'.join([f'/{i.id}' for i in users])
		for i in users:
			btn = InlineKeyboardButton(repr(i), callback_data=build_callback('select_user', i.tg_id))
			markup.add(btn)
		bot.send_message(message.chat.id, 'Выбери пользователя для редактирования:', reply_markup=markup)
	else:
		bot.send_message(message.chat.id, repr(user))


def handle_toggle_is_admin(call, tg_id):
	session = Session()
	selected_user = session.query(User).filter(User.tg_id == tg_id).first()
	selected_user.is_admin = not selected_user.is_admin
	session.add(selected_user)
	session.commit()
	bot.answer_callback_query(
		call.id,
		f'Selected user {selected_user} is {"" if selected_user.is_admin else " NOT"} an admin now'
	)
	bot.send_message(
		call.message.chat.id,
		f'Selected user {selected_user} is {"" if selected_user.is_admin else " NOT"} an admin now'
	)


def handle_toggle_is_interviewer(call, tg_id):
	session = Session()
	selected_user = session.query(User).filter(User.tg_id == tg_id).first()
	selected_user.is_interviewer = not selected_user.is_interviewer
	session.add(selected_user)
	session.commit()
	bot.answer_callback_query(
		call.id,
		f'Selected user {selected_user} is {"" if selected_user.is_interviewer else " NOT"} an interviewer now'
	)
	bot.send_message(
		call.message.chat.id,
		f'Selected user {selected_user} is {"" if selected_user.is_interviewer else " NOT"} an interviewer now'
	)


def handle_assign_to_projects(call, tg_id):
	session = Session()
	projects = session.query(Questionnaire).all()
	markup = InlineKeyboardMarkup()
	for i in projects:
		btn_project = InlineKeyboardButton(repr(i), callback_data='dummy')
		btn_interviever = InlineKeyboardButton('as interviewer',
		                                       callback_data=build_callback('assign_user_to_project', tg_id, i.id))
		btn_admin = InlineKeyboardButton('as admin',
		                                 callback_data=build_callback('assign_admin_to_project', tg_id, i.id))
		markup.add(btn_project)
		markup.add(btn_interviever, btn_admin)
	bot.send_message(call.message.chat.id, 'Select projects to toggle for assignment:', reply_markup=markup)


def handle_assign_user_to_project(call, tg_id, project_id):
	session = Session()
	selected_user = session.query(User).filter(User.tg_id == tg_id).first()
	selected_project = session.query(Questionnaire).filter(Questionnaire.id == project_id).first()
	if selected_project in selected_user.available_questionnaires:
		selected_user.available_questionnaires.remove(selected_project)
		bot.answer_callback_query(call.id, f'{selected_user} is NOT an interviewer in {selected_project}')
		bot.send_message(call.message.chat.id, f'{selected_user} is NOT an interviewer in {selected_project}')
	else:
		selected_user.available_questionnaires.append(selected_project)
		bot.answer_callback_query(call.id, f'{selected_user} IS an interviewer in {selected_project}')
		bot.send_message(call.message.chat.id, f'{selected_user} IS an interviewer in {selected_project}')
	session.add(selected_user)
	session.commit()


def handle_assign_admin_to_project(call, tg_id, project_id):
	session = Session()
	selected_user = session.query(User).filter(User.tg_id == tg_id).first()
	selected_project = session.query(Questionnaire).filter(Questionnaire.id == project_id).first()
	if selected_project in selected_user.admin_of_projects:
		selected_user.admin_of_projects.remove(selected_project)
		bot.answer_callback_query(call.id, f'{selected_user} is NOT an admin in {selected_project}')
		bot.send_message(call.message.chat.id, f'{selected_user} is NOT an admin in {selected_project}')
	else:
		selected_user.admin_of_projects.append(selected_project)
		bot.answer_callback_query(call.id, f'{selected_user} IS an admin in {selected_project}')
		bot.send_message(call.message.chat.id, f'{selected_user} IS an admin in {selected_project}')
	session.add(selected_user)
	session.commit()


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
	if call.data == 'dummy':
		print('No call data')
		return
	user = get_user(call)
	print(call)
	# with open(TMP_FILE, 'w') as out:
	# 	out.write(str(call))

	if user.is_admin or user.is_root:
		callback = json.loads(call.data)
		action = callback.get('action')
		if action == 'select_user':
			# tg_id = callback.get('kwargs').get('selected_user_id')
			tg_id = callback.get('args')[0]
			bot.answer_callback_query(call.id, f'Selected user #{tg_id}')
			handle_edit(call, selected_user_id=tg_id)
		elif action == 'toggle_is_admin':
			handle_toggle_is_admin(call, *callback.get('args'))
		elif action == 'toggle_is_interviewer':
			handle_toggle_is_interviewer(call, *callback.get('args'))
		elif action == 'assign_to_projects':
			handle_assign_to_projects(call, *callback.get('args'))
		elif action == 'assign_user_to_project':
			handle_assign_user_to_project(call, *callback.get('args'))
		elif action == 'assign_admin_to_project':
			handle_assign_admin_to_project(call, *callback.get('args'))
		else:
			bot.send_message(call.message.chat.id, 'No actions available')
		return
	bot.send_message(call.message.chat.id, 'No actions available')


def handle_edit(call, **kwargs):
	session = Session()
	user = get_user(call, session=session)
	selected_user = session.query(User).filter(User.tg_id == kwargs.get('selected_user_id')).first()
	if user.is_admin or user.is_root:
		list_display = lambda iterable: '[\n\t' + ",\n\t".join([repr(i) for i in iterable]) + '\n]'
		fields = {
			'telegram_id': selected_user.tg_id,
			'first_name': selected_user.first_name,
			'last_name': selected_user.last_name,
			'is admin': selected_user.is_admin,
			'is interviewer': selected_user.is_interviewer,
			'projects': list_display(selected_user.available_questionnaires),
			'admin_of': list_display(selected_user.admin_of_projects)
		}

		markup = InlineKeyboardMarkup(row_width=2)
		btn_is_admin = InlineKeyboardButton('Toggle: is admin', callback_data=build_callback('toggle_is_admin', selected_user.tg_id))
		btn_is_interviewer = InlineKeyboardButton('Toggle: is interviewer', callback_data=build_callback('toggle_is_interviewer', selected_user.tg_id))
		markup.add(btn_is_admin, btn_is_interviewer)
		btn_assign_to_projects = InlineKeyboardButton('Assign to projects', callback_data=build_callback('assign_to_projects', selected_user.tg_id))
		markup.add(btn_assign_to_projects)
		# btn_assign_admin = InlineKeyboardButton('Assign as admin', callback_data=build_callback('assign_admin', selected_user.tg_id))
		# markup.add(btn_assign_admin)

		msg = []
		msg.append(f'Editing {repr(selected_user)}:')
		for k, v in fields.items():
			msg.append(f'{k}: {v}')
		bot.send_message(call.message.chat.id, '\n'.join(msg), reply_markup=markup)



@bot.message_handler(commands=['users'])
def handle_users(message):
	user = get_user(message)
	if user.is_admin or user.is_root:
		session = Session()
		users = session.query(User).all()
		bot.send_message(message.chat.id, '\n'.join([repr(i) for i in users]))
	else:
		bot.send_message(message.chat.id, repr(user))


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
			'manage': 'Раздать права всякие',
		})
	bot.send_message(message.chat.id, '\n'.join([f'/{k} - {v}' for k, v in cmds.items()]))



@bot.message_handler(commands=['start'])
def handle_start(message):
	bot.send_message(message.chat.id, 'Привет! Я - Polly, бот для проведения опросов!')
	get_user(message)
	handle_help(message)
	return


@bot.message_handler(commands=['cancel'])
def handle_start(message):
	bot.send_message(message.chat.id, 'Ok, вернемся в начало.')
	handle_help(message)
	return


@bot.message_handler(commands=['surveys'])
def handle_start(message, *args, **kwargs):
	user = get_user(message)
	surveys = '\n'.join(str(i) for i in user.available_questionnaires)
	bot.send_message(message.chat.id, f'Доступно {len(user.available_questionnaires)}:\n{surveys}')


def start_survey(message, *args, **kwargs):
	session = Session()
	question = session.query(Question).filter(Question.step == 1).first()  # todo change to step = 1
	bot.send_message(message.chat.id, f'Question: {question.code}, step: {question.route_step.step}, START')
	msg = bot.send_message(message.chat.id, question.text, reply_markup=get_markup(question), )
	if question.type == types.info:
		time.sleep(SLEEP_AFTER_INFO)
		handle_answer(msg, question=question)
		return
	bot.register_next_step_handler(msg, handle_answer, question=question)


def check_data(question, message):
	if question.type == types.location and message.content_type != types.location:
		# print('check_data')
		raise DataCheckError('Location error')
	if question.type == types.categorical:
		for i in question.categories:
			if i.text == message.text:
				return True
		raise DataCheckError('Category doesn\'t exist error')
	return True


def handle_save(question, message): #todo hadle all saves to db
	if not question.save_in_survey:
		return
	check_data(question, message)
	if question.type == types.location:
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
		terminate(message)



	try:
		handle_save(question, message)
	except DataCheckError as e:
		bot.send_message(message.chat.id, e.msg)
		msg = bot.send_message(message.chat.id, question.text, reply_markup=get_markup(question), )
		bot.register_next_step_handler(msg, handle_answer, question=question)
		return

	# after_question_ask(question, message)

	bot.send_message(message.chat.id, f'Question: {question.code}, step: {question.route_step.step}, END')

	question = get_next_question(question)

	if not question:
		terminate(message)

	try:
		bot.send_message(message.chat.id, f'Question: {question.code}, step: {question.route_step.step}, START')
	except AttributeError:
		terminate(message)

	# before_question_ask(question, message)

	if question.type == types.info:
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
	return session.query(Question).filter(Question.step == question.route_step.step + 1).first()


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
