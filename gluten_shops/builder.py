from survey.models import Question, Category, location, photo, categorical, info, text, Session, Questionnaire, Route

from operator import and_

from sqlalchemy.exc import IntegrityError

QUESTIONNAIRE_VERSION = 1
QUESTIONNAIRE_NAME = 'gluten_shops'
QUESTIONNAIRE_DESCRIPTION = 'Исследование магазинов с безглютеновой продукцией'
ROUTE_VERSION = QUESTIONNAIRE_VERSION
ROUTE_STEP = 1
CATEGORY_CODE_START = 1
ALLOW_OVERWRITE = True

session = Session()


def get_questionnaire():
	quest = session.query(Questionnaire).filter(and_(Questionnaire.name == QUESTIONNAIRE_NAME, Questionnaire.version == QUESTIONNAIRE_VERSION)).first()
	if not quest:
		quest = Questionnaire()
		quest.name = QUESTIONNAIRE_NAME
		quest.description = QUESTIONNAIRE_DESCRIPTION
		quest.version = QUESTIONNAIRE_VERSION
		session.add(quest)
		session.commit()
	return quest


questionnaire = get_questionnaire()


def save(q):
	global ROUTE_STEP
	# global CATEGORY_CODE
	# global q
	# print(globals())

	q.questionnaire = questionnaire
	q.route_step = Route(step=ROUTE_STEP, version=ROUTE_VERSION)
	q.save_in_survey = q.type != 'info'
	category_code = CATEGORY_CODE_START
	for i in q.categories:
		i.code = i.code if i.code else category_code
		session.add(i)
		category_code += 1
	session.add(q)
	if ALLOW_OVERWRITE:
		try:
			session.commit()
			print(f'{q.code} created')
		except IntegrityError:
			session.rollback()
			print(f'{q.code} already in database')
			session.delete(session.query(Question).filter(
				and_(Question.code == q.code, Question.questionnaire_id == questionnaire.id)).first())
			session.commit()
			print(f'{q.code} deleted')
			session.add(q)
			session.commit()
			print(f'{q.code} created')
	else:
		session.commit()
	ROUTE_STEP += 1















#
#
# Here go questions:
#
#
q = Question()
q.code = 'q0'
q.type = info
q.text = 'This is q0. A start of everything. Literally...'
save(q)

q = Question()
q.code = 'q1'
q.type = info
q.text = 'Привет, исследователь! Надеюсь, твой гаджет хорошо заряжен, и в нем достаточно свободной памяти. Тебе предстоит сделать много фоток и нагулять хороший аппетит😄     Будь внимателен! Посмотри дважды, прежде чем ответить или сделать фото👀    Если сомневаешься, все равно фоткай. Да пребудет с тобой Сила Киноа!🙌'
save(q)

q = Question()
q.code = 'q2'
q.type = location
q.text = 'Нажми на кнопку, чтобы отправить геолокацию, и я узнаю, в каком ты сейчас магазине'
cats = [Category(text='Отправить местоположение'), ]
q.categories = cats
save(q)

q = Question()
q.code = 'qq2'
q.type = categorical
q.text = 'Kukusiki'
cats = [
	Category(text='Mur', code='MAAAU'),
	Category(text='Miu'),
	Category(text='MAU'),
	Category(text='RRRRRR'),
]
q.categories = cats
save(q)



q = Question()
q.code = 'q3'
q.type = photo
q.text = 'А еще сфоткай, пожалуйста, как выглядит вход в магазин с улицы'
save(q)

q = Question()
q.code = 'q4'
q.type = photo
q.text = 'Ты уже внутри? Сделай фото прикассовой зоны, я посмотрю чисто и красиво ли там'
save(q)

q = Question()
q.code = 'q5'
q.type = categorical
q.text = 'Принято! Теперь иди в отдел бакалеи. Найди стеллаж с макаронами/пастой   Посмотри есть ли там продукты без глютена? '
cats = [Category(text='Да'), Category(text='Нет'), ]
q.categories = cats
save(q)

q = Question()
q.code = 'q6'
q.type = categorical
q.text = '{}q6q6q6{wow}6q6q6q6{end}'
cats = [
	Category(text='Да'), Category(text='Нет'),
	Category(text='Q'), Category(text='W'),
	Category(text='E'), Category(text='R'),
]
q.categories = cats
save(q)



print('Success!!!')