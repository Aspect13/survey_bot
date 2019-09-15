import logging
import ssl
import sys

from aiohttp import web
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from settings import API_TOKEN, WEBHOOK_URL_BASE, WEBHOOK_URL_PATH, WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV, \
	WEBHOOK_LISTEN, WEBHOOK_PORT, PROXY
from survey.models import location, categorical

logger = telebot.logger
handler = logging.StreamHandler(sys.stdout)
telebot.logger.addHandler(handler)
telebot.logger.setLevel(logging.INFO)

telebot.apihelper.proxy = PROXY
bot = telebot.TeleBot(API_TOKEN)


# Process webhook calls
async def handle(request):
	print('handle', request)
	if request.match_info.get('token') == bot.token:
		request_body_dict = await request.json()
		update = telebot.types.Update.de_json(request_body_dict)
		bot.process_new_updates([update])
		return web.Response()
	else:
		return web.Response(status=403)


def run_webhook():
	app = web.Application()
	app.router.add_post('/{token}/', handle)

	# Build ssl context
	context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
	context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

	# Remove webhook, it fails sometimes the set if there is a previous webhook
	bot.remove_webhook()
	# Set webhook
	bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
	                certificate=open(WEBHOOK_SSL_CERT, 'r'))
	# Start aiohttp server
	web.run_app(
		app,
		host=WEBHOOK_LISTEN,
		port=WEBHOOK_PORT,
		ssl_context=context,
		access_log=sys.stdout
	)


def run_polling():
	bot.remove_webhook()
	# Enable saving next step handlers to file "./.handlers-saves/step.save".
	# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
	# saving will hapen after delay 2 seconds.
	bot.enable_save_next_step_handlers(delay=2)

	# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
	# WARNING It will work only if enable_save_next_step_handlers was called!
	bot.load_next_step_handlers()
	bot.polling(none_stop=True, timeout=123)


def get_markup(q):
	# if q.type == info or q.type == photo:
	# 	return ReplyKeyboardRemove()
	if q.type == location:
		markup = ReplyKeyboardMarkup(one_time_keyboard=True)
		buttons = KeyboardButton(text=q.categories[0].text, request_location=True)
		markup.add(buttons)
		return markup
	if q.type == categorical:
		markup = ReplyKeyboardMarkup(one_time_keyboard=True)
		buttons = (KeyboardButton(text=i.text) for i in q.categories)
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
