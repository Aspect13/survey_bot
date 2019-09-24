from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from survey.models import Session, User, Questionnaire
from tg_bot.helper import build_callback
from tg_bot.server import bot


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


def warn_admins(text, session=None):
	if not session:
		session = Session()
	admins = session.query(User).filter(User.is_admin).all()
	for user in admins:
		# bot.send_message(user.chat_id, text)
		bot.send_message(user.tg_id, text)


@bot.message_handler(commands=['users'])
def handle_users(message):
	user = get_user(message)
	if user.is_admin or user.is_root:
		session = Session()
		users = session.query(User).all()
		bot.send_message(message.chat.id, '\n'.join([repr(i) for i in users]))
	else:
		bot.send_message(message.chat.id, repr(user))


@bot.message_handler(commands=['manage_users'])
def handle_manage_users(message):
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


@bot.message_handler(commands=['manage_projects'])
def handle_manage_projects(message):
	user = get_user(message)
	markup = InlineKeyboardMarkup()
	if user.is_admin or user.is_root:
		projects = user.available_questionnaires
	else:
		projects = user.admin_of_projects
	for i in projects:
		btn = InlineKeyboardButton(repr(i), callback_data=build_callback('select_project', i.id))
		markup.add(btn)
	bot.send_message(message.chat.id, 'Выбери проект для редактирования:', reply_markup=markup)


def handle_user_edit(call, tg_id):
	bot.answer_callback_query(call.id, f'Selected user #{tg_id}')
	session = Session()
	user = get_user(call, session=session)
	selected_user = session.query(User).filter(User.tg_id == tg_id).first()
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
		btn_is_admin = InlineKeyboardButton('Toggle: is admin',
		                                    callback_data=build_callback('toggle_is_admin', selected_user.tg_id))
		btn_is_interviewer = InlineKeyboardButton('Toggle: is interviewer',
		                                          callback_data=build_callback('toggle_is_interviewer',
		                                                                       selected_user.tg_id))
		markup.add(btn_is_admin, btn_is_interviewer)
		btn_assign_to_projects = InlineKeyboardButton('Assign to projects',
		                                              callback_data=build_callback('assign_to_projects',
		                                                                           selected_user.tg_id))
		markup.add(btn_assign_to_projects)
		# btn_assign_admin = InlineKeyboardButton('Assign as admin', callback_data=build_callback('assign_admin', selected_user.tg_id))
		# markup.add(btn_assign_admin)

		msg = []
		msg.append(f'Editing {repr(selected_user)}:')
		for k, v in fields.items():
			msg.append(f'{k}: {v}')
		bot.send_message(call.message.chat.id, '\n'.join(msg), reply_markup=markup)


def handle_toggle_is_admin(call, tg_id):
	session = Session()
	selected_user = session.query(User).filter(User.tg_id == tg_id).first()
	selected_user.is_admin = not selected_user.is_admin
	session.add(selected_user)
	session.commit()
	msg = f'Selected user {selected_user} is {"" if selected_user.is_admin else " NOT"} an admin now'
	bot.answer_callback_query(call.id, msg)
	bot.send_message(call.message.chat.id, msg)


def handle_toggle_is_interviewer(call, tg_id):
	session = Session()
	selected_user = session.query(User).filter(User.tg_id == tg_id).first()
	selected_user.is_interviewer = not selected_user.is_interviewer
	session.add(selected_user)
	session.commit()
	msg = f'Selected user {selected_user} is {"" if selected_user.is_interviewer else " NOT"} an interviewer now'
	bot.answer_callback_query(call.id, msg)
	bot.send_message(call.message.chat.id, msg)


def handle_assign_to_projects(call, tg_id):
	session = Session()
	projects = session.query(Questionnaire).all()
	markup = InlineKeyboardMarkup()
	for i in projects:
		btn_project = InlineKeyboardButton(
			f'{repr(i)} [tap to edit]',
			callback_data=build_callback('handle_project_edit', i.id)
		)
		btn_interviewer = InlineKeyboardButton(
			'as interviewer',
			callback_data=build_callback('assign_user_to_project', tg_id, i.id)
		)
		btn_admin = InlineKeyboardButton(
			'as admin',
			callback_data=build_callback('assign_admin_to_project', tg_id, i.id)
		)
		markup.add(btn_project)
		markup.add(btn_interviewer, btn_admin)
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





def handle_project_edit(call, project_id):
	bot.answer_callback_query(call.id, f'Selected project #{project_id}')
	session = Session()
	user = get_user(call, session=session)
	selected_project = session.query(Questionnaire).filter(Questionnaire.id == project_id).first()
	if user.is_admin or user.is_root or user in selected_project.project_admins:
		# list_display = lambda iterable: '[\n\t' + ",\n\t".join([repr(i) for i in iterable]) + '\n]'
		fields = {
			'name': selected_project.name,
			'description': selected_project.description,
			'version': selected_project.version,
			'is active': selected_project.is_active,
			'created by': repr(selected_project.created_by),
		}

		markup = InlineKeyboardMarkup(row_width=2)
		btn_is_active = InlineKeyboardButton('Toggle: is active', callback_data=build_callback('toggle_is_active', project_id))
		markup.add(btn_is_active)
		btn_assign_users = InlineKeyboardButton(
			'Assign interviewers',
			callback_data=build_callback('assign_users', project_id)
		)
		markup.add(btn_assign_users)

		msg = []
		msg.append(f'Editing {repr(selected_project)}:')
		for k, v in fields.items():
			msg.append(f'{k}: {v}')
		bot.send_message(call.message.chat.id, '\n'.join(msg), reply_markup=markup)


def handle_toggle_is_active(call, project_id):
	session = Session()
	selected_project = session.query(Questionnaire).filter(Questionnaire.id == project_id).first()
	selected_project.is_active = not selected_project.is_active
	session.add(selected_project)
	session.commit()
	msg = f'Selected project {selected_project} is {"active" if selected_project.is_active else "inactive"} now'
	bot.answer_callback_query(call.id, msg)
	bot.send_message(call.message.chat.id, msg)


def handle_assign_users(call, project_id):
	session = Session()
	users = session.query(User).all()
	markup = InlineKeyboardMarkup()
	for i in users:
		btn_user = InlineKeyboardButton(
			f'{repr(i)} [tap to edit]',
			callback_data=build_callback('handle_user_edit', i.id)
		)
		btn_interviewer = InlineKeyboardButton(
			'as interviewer',
			callback_data=build_callback('assign_user_to_project', i.tg_id, project_id)
		)
		btn_admin = InlineKeyboardButton(
			'as admin',
			callback_data=build_callback('assign_admin_to_project', i.tg_id, project_id)
		)
		markup.add(btn_user)
		markup.add(btn_interviewer, btn_admin)
	bot.send_message(call.message.chat.id, 'Select users to toggle for assignment:', reply_markup=markup)
