import json

import telebot
from telebot import types

from models import User
from settings import API_TOKEN
from utils import get_distance
from webhook import bot, run_polling

# markup_yes_no = types.ReplyKeyboardMarkup(one_time_keyboard=True)
markup_yes_no = types.InlineKeyboardMarkup()
btn_yes = types.InlineKeyboardButton('Да', callback_data='cb_yes')
btn_no = types.InlineKeyboardButton('Нет', callback_data='cb_no')
markup_yes_no.add(btn_yes, btn_no)






@bot.message_handler(commands=['start'])
def handle_q1(message):
	bot.send_message(message.chat.id, 'q1', reply_markup=markup_yes_no,)
	# bot.register_next_step_handler(msg, process_name_step)

	# bot.register_next_step_handler(msg, handle_q2)


def handle_q2(message, clear_markup=True):
	print(message)
	with open('tmp.json', 'w') as out:
		out.write(str(message))
	# json.dump(str(message).replace("'", '"'), )
	bot.send_message(message.chat.id, 'q2', reply_markup=markup_yes_no)
	# bot.register_next_step_handler(msg, process_name_step)


tmp_d = {'q1': handle_q1, 'q2': handle_q2}


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
	print(call)
	with open('tmp.json', 'w') as out:
		out.write(str(call))
	if call.data == "cb_yes":
		bot.answer_callback_query(call.id, "Answer is Yes")
	elif call.data == "cb_no":
		bot.answer_callback_query(call.id, "Answer is No")
	try:
		key_lst = list(tmp_d.keys())
		this_q_index = key_lst.index(call.message.text)
		next_q_name = key_lst[this_q_index + 1]
		tmp_d[next_q_name](call.message)
	except (ValueError, IndexError):
		bot.send_message(call.message.chat.id, 'That is all over')







if __name__ == '__main__':


	# Enable saving next step handlers to file "./.handlers-saves/step.save".
	# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
	# saving will hapen after delay 2 seconds.
	# bot.enable_save_next_step_handlers(delay=2)

	# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
	# WARNING It will work only if enable_save_next_step_handlers was called!
	# bot.load_next_step_handlers()
	run_polling()

