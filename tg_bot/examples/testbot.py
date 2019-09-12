from telebot import types

from models import User
from utils import get_distance
from webhook import bot, run_polling


# telebot.apihelper.proxy = {'https': 'socks5h://127.0.0.1:9150'}
# bot = telebot.TeleBot(API_TOKEN)
# bot.remove_webhook()


# keyboard1 = telebot.types.ReplyKeyboardMarkup()
# keyboard1.row('Привет', 'Пока')
#
#
# @bot.message_handler(commands=['start'])
# def start_message(message):
# 	bot.send_message(message.chat.id, 'What\'s up', reply_markup=keyboard1)


# @bot.message_handler(content_types=['text'])
# @bot.message_handler()
# def send_text(message):
#
# 	if message.text.lower() == 'привет':
# 		bot.send_message(message.chat.id, 'Привет, мой создатель')
# 	elif message.text.lower() == 'пока':
# 		bot.send_message(message.chat.id, 'Прощай, создатель')
# 	elif message.text.lower() == 'yo':
# 		bot.send_sticker(message.chat.id, 'CAADAgADKAMAAoZALgI8Cc13uyaJLhYE')
#
# 	print(message)
# 	json.dump(str(message), open('tmp.json', 'w'))
#
#









@bot.message_handler(content_types=['sticker'])
def sticker_id(message):
	# json.dump(json.loads(str(message)), open('tmp.json', 'w'))
	print(message.sticker.file_id)










@bot.message_handler(commands=['purge'])
def purge(message):
	user = User(message.from_user)
	if user.existed:
		user.purge()
		bot.send_message(message.chat.id, 'You were deleted')
	else:
		bot.send_message(message.chat.id, 'Nothing to delete')


@bot.message_handler(commands=['self'])
def show_info(message):
	user = User(message.from_user)
	if user.existed:
		bot.send_message(message.chat.id, repr(user))
	else:
		bot.send_message(message.chat.id, 'No information about you, try /start')


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
	user = User(message.from_user)
	user.save()

	markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
	markup.one_time_keyboard = True
	# types.ReplyKeyboardRemove
	markup.add('Ye, sure!')
	markup.add('No, with surname please')
	markup.add('No, I\'ll tell you how')

	msg = bot.send_message(message.chat.id, f"""\
Greetings {user.preferred_name}, I am polly, an example bot.
May I call you {user.first_name}?
""", reply_markup=markup)
	# bot.register_next_step_handler(msg, process_name_step)

	bot.register_next_step_handler(msg, process_greetings_step)


def process_greetings_step(message):
	try:
		user = User(message.from_user)

		if message.text == 'Ye, sure!':
			user.preferred_name = user.first_name
			user.save()
			msg = bot.send_message(message.chat.id, f'How old are you, {user.preferred_name}?', reply_markup=types.ReplyKeyboardRemove())
			bot.register_next_step_handler(msg, process_age_step)
		elif message.text == 'No, with surname please':
			msg = bot.send_message(message.chat.id, f'How old are you, {user.preferred_name}?', reply_markup=types.ReplyKeyboardRemove())
			bot.register_next_step_handler(msg, process_age_step)
		elif message.text == 'No, I\'ll tell you how':
			msg = bot.reply_to(message, 'Ok, I\'m listening...', reply_markup=types.ReplyKeyboardRemove())
			bot.register_next_step_handler(msg, process_greetings_step_other)
		else:
			raise Exception()

	except Exception as e:
		print(e)
		bot.send_sticker(message.chat.id, 'CAADAgADKAMAAoZALgI8Cc13uyaJLhYE')
		bot.reply_to(message, 'oooops')


def process_greetings_step_other(message):
	try:
		user = User(message.from_user)
		user.preferred_name = message.text
		user.save()
		bot.send_message(message.chat.id, f'Great! From now on you are {user.preferred_name} to me')
		msg = bot.reply_to(message, f'How old are you, {user.preferred_name}?')
		bot.register_next_step_handler(msg, process_age_step)
	except Exception as e:
		print(e)
		bot.send_sticker(message.chat.id, 'CAADAgADKAMAAoZALgI8Cc13uyaJLhYE')
		bot.reply_to(message, 'oooops')


# def process_name_step(message):
# 	try:
# 		chat_id = message.chat.id
# 		name = message.text
# 		user = User(name)
# 		user_dict[chat_id] = user
# 		msg = bot.reply_to(message, 'How old are you?')
# 		bot.register_next_step_handler(msg, process_age_step)
# 	except Exception as e:
# 		bot.reply_to(message, 'oooops')


def process_age_step(message):
	try:
		age = message.text
		if not age.isdigit():
			msg = bot.reply_to(message, 'Age should be a number. How old are you?')
			bot.register_next_step_handler(msg, process_age_step)
			return

		user = User(message.from_user)
		user.age = age
		user.save()

		markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
		markup.add('Male', 'Female')
		msg = bot.send_message(message.chat.id, 'What is your gender', reply_markup=markup)
		bot.register_next_step_handler(msg, process_sex_step)
	except Exception as e:
		print(e)
		bot.send_sticker(message.chat.id, 'CAADAgADKAMAAoZALgI8Cc13uyaJLhYE')
		bot.reply_to(message, 'oooops')


def process_sex_step(message):
	try:
		sex = message.text
		user = User(message.from_user)
		if (sex == u'Male') or (sex == u'Female'):
			user.sex = sex
			user.save()
		else:
			raise Exception()
		bot.send_message(message.chat.id, 'Nice to meet you, ' + user.preferred_name + '\n Age:' + str(user.age) + '\n Sex:' + user.sex)
		bot.send_sticker(message.chat.id, 'CAADAgADJgMAAoZALgIZC2GLq2N1rhYE')

		bot.send_message(message.chat.id, f'\nOk, {user.preferred_name}, Let\'s start a small survey now!\n')

		markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
		button_geo = types.KeyboardButton(text='Отправить местоположение', request_location=True)
		markup.add(button_geo)
		msg = bot.send_message(message.chat.id, f'{user.preferred_name}, где ты находишься? (Нажми на кнопку, чтобы отправить геолокацию)', reply_markup=markup)
		bot.register_next_step_handler(msg, process_location)
	except Exception as e:
		print(e)
		bot.send_sticker(message.chat.id, 'CAADAgADKAMAAoZALgI8Cc13uyaJLhYE')
		bot.reply_to(message, 'oooops')


@bot.message_handler(content_types=['location'])
def process_location(message):
	user = User(message.from_user)
	user.latitude = message.location.latitude
	user.longitude = message.location.longitude
	user.save()
	dist = round(get_distance(user.latitude, user.longitude), 1)
	bot.send_message(message.chat.id, f'Ого, ты в {dist}км от центра Москвы!')

	bot.send_message(message.chat.id, '\nТеперь к делу...')
	msg = bot.send_message(message.chat.id, f'{user.preferred_name}, в каком отделов магазина размещена безглютеновая продукция?', reply_markup=types.ReplyKeyboardRemove())
	bot.register_next_step_handler(msg, process_q1)
	# msg = bot.send_message(message.chat.id, f'\n{user.preferred_name}, а теперь отправь мне красивую фотографию')
	# bot.register_next_step_handler(msg, process_photo)


def process_q1(message):
	user = User(message.from_user)
	user.q1 = message.text
	user.save()

	markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
	markup.add('Да', 'Нет')
	msg = bot.send_message(message.chat.id, f'Круто, мой любимый отдел, кстати! ;)\nА выделяется ли стеллаж с безглютеновой продукцией от остальных стеллажей?', reply_markup=markup)
	bot.register_next_step_handler(msg, process_q2)


def process_q2(message):
	user = User(message.from_user)
	if message.text == u'Да' or message.text == u'Нет':
		user.q2 = message.text
		user.save()
	else:
		bot.send_message(message.chat.id, 'Error - if u see this, text AD')
		return

	markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
	markup.add('Верхние полки')
	markup.add('По середине - на уровне глаз')
	markup.add('Нижние полки')
	msg = bot.send_message(message.chat.id, 'Супер! И еще: На каком уровне размещены безглютеновые продукты?', reply_markup=markup)
	bot.register_next_step_handler(msg, process_q3)


def process_q3(message):
	user = User(message.from_user)
	user.q3 = message.text
	user.save()
	msg = bot.send_message(message.chat.id, f'\n{user.preferred_name}, ты молодец!\nА теперь отправь мне красивую фотографию', reply_markup=types.ReplyKeyboardRemove())
	bot.register_next_step_handler(msg, process_photo)


@bot.message_handler(content_types=['photo'])
def process_photo(message):
	user = User(message.from_user)
	# json.dump(str(message), open('tmp.json', 'w'))
	if message.content_type != 'photo':
		msg = bot.send_message(message.chat.id, f'Не, мне нужна фотография',)
		bot.register_next_step_handler(msg, process_photo)
		return
	file_info = bot.get_file(message.photo[-1].file_id)
	print(file_info)
	downloaded_file = bot.download_file(file_info.file_path)
	tmp = file_info.file_path.split('/')
	file_path = tmp[0] + '/' + user.id + '_' + tmp[1]
	with open(file_path, 'wb') as out:
		out.write(downloaded_file)

	user.photos.append(file_path)
	user.save()
	bot.send_message(message.chat.id, f'{user.preferred_name}, спасибо, фотка сохранена под именем: {file_path}')
	bot.send_message(message.chat.id, f'\nНа этом пока всё! Можно начать заново \n/start\n или показать информацию о себе \n/self\n можно также удалить всю информацию о себе \n/purge')


	# user = User(message.from_user)
	# user.latitude = message.location.latitude
	# user.longitude = message.location.longitude
	# user.save()
	# dist = round(get_distance(user.latitude, user.longitude), 1)
	# bot.send_message(message.chat.id, f'Ого, ты в {dist}км от центра Москвы!')
	#
	# markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
	# button_geo = types.InputMediaPhoto()
	# markup.add(button_geo)
	# msg = bot.send_message(message.chat.id,
	#                        f'{user.preferred_name}, где ты находишься? (Нажми на кнопку, чтобы отправить геолокацию)',
	#                        reply_markup=markup)
	# bot.register_next_step_handler(msg, process_location)


# @bot.message_handler(commands=["geo"])
# def geo(message):
#
# 	keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
# 	button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
# 	keyboard.add(button_geo)
# 	bot.send_message(message.chat.id, "Привет! Нажми на кнопку и передай мне свое местоположение", reply_markup=keyboard)
#
#
# @bot.message_handler(content_types=["location"])
# def location(message):
# 	if message.location is not None:
# 		print(message.location)
# 		print("latitude: %s; longitude: %s" % (message.location.latitude, message.location.longitude))


if __name__ == '__main__':

	# Enable saving next step handlers to file "./.handlers-saves/step.save".
	# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
	# saving will hapen after delay 2 seconds.
	bot.enable_save_next_step_handlers(delay=2)

	# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
	# WARNING It will work only if enable_save_next_step_handlers was called!
	bot.load_next_step_handlers()
	run_polling()