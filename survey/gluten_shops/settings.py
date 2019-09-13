from operator import and_

from sqlalchemy.exc import IntegrityError

from survey.models import Question, Session, Questionnaire, Route

QUESTIONNAIRE_VERSION = 1
QUESTIONNAIRE_NAME = 'gluten_shops'
QUESTIONNAIRE_DESCRIPTION = 'Исследование магазинов с безглютеновой продукцией'
ROUTE_VERSION = 1
ROUTE_STEP = 1
CATEGORY_CODE_START = 1
CATEGORY_CODE = CATEGORY_CODE_START


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


def save(custom_route_step=-1):
	global ROUTE_STEP
	global CATEGORY_CODE
	global q
	q.questionnaire = questionnaire
	q.route_step = Route(step=custom_route_step if custom_route_step else ROUTE_STEP, version=ROUTE_VERSION)
	q.save_in_survey = q.type != 'info'
	CATEGORY_CODE = CATEGORY_CODE_START
	for i in q.categories:
		i.code = CATEGORY_CODE
		session.add(i)
		CATEGORY_CODE += 1
	session.add(q)
	# session.commit()
	try:
		session.commit()
		print(f'{q.code} created')
	except IntegrityError:
		print(f'{q.code} already in database')
		session.rollback()
		q = session.query(Question).filter(Question.code == q.code).first()
	if not custom_route_step:
		ROUTE_STEP += 1
