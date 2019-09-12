from operator import and_

from sqlalchemy.exc import IntegrityError

from models import Session, Question, Category, Route, Questionnaire, Survey


QUESTIONNAIRE_VERSION = 1
QUESTIONNAIRE_NAME = 'Gluten shops'
ROUTE_VERSION = 1
ROUTE_STEP = 1
info = 'info'
categorical = 'categorical'
photo = 'photo'
location = 'location'

session = Session()


quest = session.query(Questionnaire).filter(and_(Questionnaire.name == QUESTIONNAIRE_NAME, Questionnaire.version == QUESTIONNAIRE_VERSION)).first()
# print(quest.questions)
# session.delete(quest)
# session.commit()
# print(quest)
# exit()
if not quest:
	quest = Questionnaire()
	quest.name = QUESTIONNAIRE_NAME
	quest.version = QUESTIONNAIRE_VERSION
	session.add(quest)
	session.commit()


def save():
	global ROUTE_STEP
	global q
	q.questionnaire = quest
	q.route_step = Route(step=ROUTE_STEP, version=ROUTE_VERSION)
	q.save_in_survey = q.type != 'info'
	for i in q.categories:
		session.add(i)
	session.add(q)
	try:
		session.commit()
		print(f'{q.code} created')
	except IntegrityError:
		print(f'{q.code} already in database')
		session.rollback()
		q = session.query(Question).filter(Question.code == q.code).first()
	ROUTE_STEP += 1




#
#
# Here go questions:
#
#
q = Question()
q.code = 'q1'
q.type = info
q.text = 'Привет, исследователь! Надеюсь, твой гаджет хорошо заряжен, и в нем достаточно свободной памяти. Тебе предстоит сделать много фоток и нагулять хороший аппетит😄     Будь внимателен! Посмотри дважды, прежде чем ответить или сделать фото👀    Если сомневаешься, все равно фоткай. Да пребудет с тобой Сила Киноа!🙌'
save()

q = Question()
q.code = 'q2'
q.type = location
q.text = 'Нажми на кнопку, чтобы отправить геолокацию, и я узнаю, в каком ты сейчас магазине'
cats = []
cats += Category(text='Отправить местоположение')
q.categories = cats
save()

q = Question()
q.code = 'q3'
q.type = photo
q.text = 'А еще сфоткай, пожалуйста, как выглядит вход в магазин с улицы'
save()

q = Question()
q.code = 'q4'
q.type = photo
q.text = 'Ты уже внутри? Сделай фото прикассовой зоны, я посмотрю чисто и красиво ли там'
save()

q = Question()
q.code = 'q5'
q.type = categorical
q.text = 'Принято! Теперь иди в отдел бакалеи. Найди стеллаж с макаронами/пастой   Посмотри есть ли там продукты без глютена? '
cats = []
cats += Category(text='Да')
cats += Category(text='Нет')
q.categories = cats
save()

