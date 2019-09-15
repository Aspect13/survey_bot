from operator import and_

from settings import CACHE_QUERIES
from survey.models import Session, Questionnaire, Question
import sys


class Routing:
	def __init__(self, questionnaire_id=None, session=None):
		self.session = session if session else Session()
		self.questionnaire_id = questionnaire_id if questionnaire_id else self.session.query(Questionnaire.id).first()[0] # todo: not first

	def __getattr__(self, item):
		if not CACHE_QUERIES:
			print('querying...')
			self.session.query(Question).filter(
				and_(Question.questionnaire_id == self.questionnaire_id, Question.code == item)
			).first()
		print(self.__dict__)
		try:
			return self.__dict__[item]
		except KeyError:
			print('querying...')
			self.__dict__[item] = self.session.query(Question).filter(
				and_(Question.questionnaire_id == self.questionnaire_id, Question.code == item)
			).first()
			return self.__dict__[item]

	def contains(self, attr, categories):
		print(attr, categories)






q = Routing(questionnaire_id=1)


q.q5.yo = 123
print('q5 cats', q.q5.categories)
for i in q.q5.categories:
	print(i)
q.q5.set_filter(func=lambda cat: cat.id % 2 == 0)
for i in q.q5.categories:
	print(i)
print('q5 cats', q.q5.categories)

# q.q6.set_filter(lambda cat: cat.code in [i.code for i in q.q5.categories])
# q.q6.set_filter(lambda cat: cat in q.q5.categories)

print(q.q6.set_filter(q.q5.categories))
print('q6 cats', q.q6.categories)
print(q.q6.set_filter([1,2,3,4]))
print('q6 cats', q.q6.categories)