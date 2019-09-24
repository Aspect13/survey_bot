import datetime

from sqlalchemy import Table, Column, MetaData, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import relationship, mapper
from sqlalchemy_utils import ChoiceType

from survey.models import engine, QuestionTypes, Session, Category, User


def create_column_types(defined_categories):
	return tuple((i, i) for i in defined_categories)


DEFAULT_COLUMNS = [
	Column('id', Integer, primary_key=True),
	Column('status', ChoiceType(create_column_types(['started', 'finished'])), default=('started', 'started')),
	Column('start_time', DateTime, default=datetime.datetime.now()),
	Column('finish_time', DateTime),
	Column('last_filled_question_name', String, default=None, nullable=True),
	Column('started_by_id', Integer, ForeignKey(User.id), nullable=False),
	# Column('questionnaire_id', Integer, ForeignKey(Questionnaire.id), nullable=False),

]

PROMISED_RELATIONSHIPS = {
	# 'questionnaire': relationship(Questionnaire, back_populates='result_table', uselist=False,),
	'started_by': relationship(User, backref='started_surveys'),
}


def promise_relationship(relationship_name, relationship_value):
	PROMISED_RELATIONSHIPS[relationship_name] = relationship_value


def generate_columns(questionnaire):
	result_table_columns = []
	for q in filter(lambda i: i.save_in_survey or i.type.code == QuestionTypes.constraint, questionnaire.questions):
		if q.type.code == QuestionTypes.text or q.type.code == QuestionTypes.photo:
			result_table_columns.append(Column(q.code, String))
		elif q.type.code == QuestionTypes.integer:
			result_table_columns.append(Column(q.code, Integer))
		elif q.type.code == QuestionTypes.location:
			result_table_columns.append(Column(f'{q.code}_latitude', Float))
			result_table_columns.append(Column(f'{q.code}_longitude', Float))
		elif q.type.code == QuestionTypes.categorical:
			# result_table_columns.append(Column(ChoiceType(create_column_types(q.categories))))
			result_table_columns.append(Column(q.code, Integer, ForeignKey(Category.id), nullable=True),)
			# result_table_columns.append(Column(f'{q.code}_id', ChoiceType(create_column_types((i.code for i in q.categories))), ForeignKey(Category.id), nullable=True),)
			promise_relationship(q.code, relationship('Category', backref='results'))
		elif q.type.code == QuestionTypes.constraint:
			print(*q.text.split(','))
			result_table_columns.append(UniqueConstraint(*q.text.split(','), name=q.code)),
		else:
			NotImplementedError(f'The {q.type.code} type is not handled!!!')
	return result_table_columns




# class Results(Base):
# 	__tablename__ = 'test1'
# 	id = Column(Integer, primary_key=True),
# 	status = Column(ChoiceType(create_column_types(['started', 'finished'])), default=('started', 'started')),
# 	start_time = Column(DateTime, default=datetime.datetime.now()),
# 	finish_time = Column(DateTime),
# 	last_filled_question_name = Column(String, default=None, nullable=True),
# 	started_by_id = Column(Integer, ForeignKey(User.id), nullable=False),
# 	started_by = relationship(User, backref='started_surveys'),











def create_result_table(questionnaire):
	metadata = MetaData()

	result_table_columns = generate_columns(questionnaire)

	print(result_table_columns)

	ResultTable = Table(
		questionnaire.results_table_name, metadata,
		*DEFAULT_COLUMNS,
		*result_table_columns,

		)

	for rel_name, rel_value in PROMISED_RELATIONSHIPS.items():
		ResultTable.__setattr__(rel_name, rel_value)

	s = Session()
	try:
		s.execute('drop table if exists {}'.format(questionnaire.results_table_name))
	except Exception as e:
		print(e)
	metadata.create_all(bind=engine, tables=[ResultTable])

	return ResultTable


# from gluten_shops.survey_script import questionnaire as qre
# tmp = create_result_table(qre)
# class Results(Base):
# 	__table__ = tmp
#
# Base.metadata.create_all(bind=engine)
# print([i for i in Base.metadata.tables])


if __name__ == '__main__':
	from gluten_shops.survey_script import questionnaire as qre
	print('READ THIS', 'https://docs.sqlalchemy.org/en/13/orm/extensions/automap.html')
	create_result_table(qre)




