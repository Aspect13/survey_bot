from sqlalchemy import Table, Column, MetaData, Integer, String, Float

from survey.models import engine, QuestionTypes, Session, Questionnaire


def create_result_table(questionnaire):



	metadata = MetaData()

	result_table_columns = []
	for q in filter(lambda i: i.save_in_survey, questionnaire.questions):
		if q.type == QuestionTypes.text:
			# print(q.code, q.type, q.text)
			result_table_columns.append(Column(q.code, String))
		elif q.type == QuestionTypes.integer:
			result_table_columns.append(Column(q.code, Integer))
		elif q.type.code == QuestionTypes.location:
			print('loc')
			result_table_columns.append(Column(f'{q.code}_latitude', Float))
			result_table_columns.append(Column(f'{q.code}_longitude', Float))

	print(result_table_columns)

	ResultTable = Table(questionnaire.results_table_name, metadata,
		Column('id', Integer, primary_key=True),
		*result_table_columns
	)

	s = Session()
	# s.delete(ResultTable)
	# s.commit()
	s.execute('drop table {}'.format(questionnaire.results_table_name))
	metadata.create_all(bind=engine, tables=[ResultTable])


if __name__ == '__main__':
	from gluten_shops.survey_script import questionnaire as qre
	create_result_table(qre)