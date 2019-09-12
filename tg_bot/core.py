import json

import telebot
from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from models import User
from settings import API_TOKEN
from utils import get_distance
from webhook import bot, run_polling

# markup_yes_no = types.ReplyKeyboardMarkup(one_time_keyboard=True)


markup_yes_no = ReplyKeyboardMarkup()
btn_yes = KeyboardButton('Да')
btn_no = KeyboardButton('Нет')
markup_yes_no.add(btn_yes, btn_no)



@bot.message_handler(content_types=['text'])
def printer(message):
	print(message.text)
	print(message)



@bot.message_handler(commands=['start'])
def handle_q1(message):
	msg = bot.send_message(message.chat.id, 'q1', reply_markup=markup_yes_no,)
	bot.register_next_step_handler(msg, handle_q2)


def handle_q2(message, clear_markup=True):
	print(message)
	with open('tmp.json', 'w') as out:
		out.write(str(message))
	# json.dump(str(message).replace("'", '"'), )
	msg = bot.send_message(message.chat.id, 'q2')
	# bot.register_next_step_handler(msg, handle_q1)


tmp_d = {'q1': handle_q1, 'q2': handle_q2}

# key_lst = list(tmp_d.keys())
# this_q_index = key_lst.index(call.message.text)
# next_q_name = key_lst[this_q_index + 1]
# tmp_d[next_q_name](call.message)







if __name__ == '__main__':


	# Enable saving next step handlers to file "./.handlers-saves/step.save".
	# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
	# saving will hapen after delay 2 seconds.
	bot.enable_save_next_step_handlers(delay=2)

	# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
	# WARNING It will work only if enable_save_next_step_handlers was called!
	bot.load_next_step_handlers()
	run_polling()

