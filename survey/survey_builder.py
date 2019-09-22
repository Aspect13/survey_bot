from operator import and_

from sqlalchemy.exc import IntegrityError

from survey.models import Session, Questionnaire, QuestionTypes, Question


def _get_questionnaire(q_name, q_version, q_description, session=None, **kwargs):
	if not session:
		session = Session()
	quest = session.query(Questionnaire).filter(
		and_(Questionnaire.name == q_name, Questionnaire.version == q_version)
	).first()
	if not quest:
		quest = Questionnaire()
		quest.name = q_name
		quest.description = q_description
		quest.version = q_version
		creator = kwargs.get('created_by')
		if creator:
			quest.created_by = creator
			quest.project_users.append(creator)
			quest.project_admins.append(creator)

		quest.results_table_name = get_result_table_name(quest)
		session.add(quest)
		session.commit()
	return quest


def _save(question, questionnaire, step=None, category_code_start=1, allow_overwrite=True, session=None):
	if not session:
		session = Session()
	question.questionnaire = questionnaire
	question.step = step
	question.save_in_survey = question.type not in (QuestionTypes.info, QuestionTypes.sticker)
	category_code = category_code_start
	for i in question.categories:
		i.code = i.code if i.code else category_code
		session.add(i)
		category_code += 1
	session.add(question)
	try:
		session.commit()
		print(f'{question.code} created')
	except IntegrityError:
		session.rollback()
		print(f'{question.code} already in database')
		if allow_overwrite:
			session.delete(session.query(Question).filter(
				and_(Question.code == question.code, Question.questionnaire_id == questionnaire.id)).first()
			)
			session.commit()
			print(f'{question.code} deleted')
			session.add(question)
			session.commit()
			print(f'{question.code} created')
	if step:
		step += 1


def get_result_table_name(questionnaire):
	return '{}_{}'.format(questionnaire.name, questionnaire.version)