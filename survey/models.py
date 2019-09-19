import json
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, DateTime, Date, Boolean, UniqueConstraint, \
	Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy_utils import ChoiceType

from settings import DB_PATH, USER_FILE

engine = create_engine(f'sqlite:///{DB_PATH}', echo=__name__ == '__main__')
# Session = sessionmaker(bind=engine)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
Base = declarative_base()


# class Survey(Base):
# 	__tablename__ = 'surveys'
#
# 	id = Column(Integer, primary_key=True)
# 	questionnaire_id = Column(Integer, ForeignKey('questionnaires.id'), nullable=False)
# 	questionnaire = relationship('Questionnaire', back_populates='surveys')


class Questionnaire(Base):
	__tablename__ = 'questionnaires'
	__table_args__ = (UniqueConstraint('version', 'name', name='uc_1'),)

	id = Column(Integer, primary_key=True)
	name = Column(String(64), nullable=False)
	description = Column(String(256), nullable=True)
	version = Column(Integer, nullable=False)
	is_available = Column(Boolean, nullable=False, default=False)

	questions = relationship('Question', back_populates='questionnaire', cascade='all, delete, delete-orphan',
	                         order_by='Question.id')
	# surveys = relationship('Survey', back_populates='questionnaire')


class QuestionTypes:
	info = 'info'
	categorical = 'categorical'
	photo = 'photo'
	location = 'location'
	text = 'text'
	dict = {
		'info': info,
		'categorical': categorical,
		'photo': photo,
		'location': location,
		'text': text,
	}

	def __getitem__(self, item, default=None):
		return self.dict.get(item, default)




class Question(Base):
	__tablename__ = 'questions'
	__table_args__ = (
		UniqueConstraint('questionnaire_id', 'code', name='uc_1'),
		UniqueConstraint('step', 'code', name='uc_2'),
	)

	# TYPES = [
	# 	(question_types['info'], question_types['info']),
	# 	(question_types['categorical'], question_types['categorical']),
	# 	(question_types['photo'], question_types['photo']),
	# 	(question_types['location'], question_types['location']),
	# 	(question_types['text'], question_types['text']),
	# ]
	# TYPES = {
	# 	'info': 'info',
	# 	'categorical': 'categorical',
	# 	'photo': 'photo',
	# 	'location': 'location',
	# 	'text': 'text',
	# }

	id = Column(Integer, primary_key=True)
	code = Column(String(64), nullable=False)
	text = Column(String(512), nullable=False, )
	type = Column(ChoiceType(QuestionTypes.dict))
	save_in_survey = Column(Boolean, nullable=False, default=True)
	step = Column(Integer, )

	categories = relationship('Category', back_populates='question', cascade='all, delete, delete-orphan', )

	# route_step = relationship('Route', back_populates='question', uselist=False, cascade='all, delete, delete-orphan')

	questionnaire_id = Column(Integer, ForeignKey('questionnaires.id'), nullable=False)
	questionnaire = relationship('Questionnaire', back_populates='questions')


	# def save(self, session=None):


	# original_categories = None

	def set_filter(self, categories=None, func=None, persist=True):
		if not self.original_categories:
			self.original_categories = self.categories
		if categories:
			# print(categories)
			self.set_filter(
				func=lambda cat: cat.code in [i.code if isinstance(i, Category) else str(i) for i in categories],
				persist=persist)
		if persist:
			self.categories = list(filter(func, self.original_categories))
		return list(filter(func, self.original_categories))

	def format_text(self, *args, **kwargs):
		return self.text.format(*args, **kwargs)

	# def contains(self, categories):
	# 	print(self.categories)
	# 	print(categories)
	# 	return lambda: cat.code in [j.code for j in categories]

	def __repr__(self):
		return f'<Question code={self.code} text={self.text[:10]}... {self.route_step}>'


class Category(Base):
	__tablename__ = 'categories'
	__table_args__ = (UniqueConstraint('question_id', 'code', name='uc_1'),)

	id = Column(Integer, primary_key=True)
	text = Column(String(256), nullable=False)
	code = Column(String(64), nullable=False)

	question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
	question = relationship('Question', back_populates='categories')

	def __repr__(self):
		return f'<Category {self.code}: {self.text}>'


# class Route(Base):
# 	__tablename__ = 'routes'
# 	__table_args__ = (UniqueConstraint('version', 'step', name='uc_1'), )
#
# 	id = Column(Integer, primary_key=True)
# 	version = Column(Integer, nullable=False)
# 	step = Column(Integer, nullable=False)
# 	question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
# 	question = relationship('Question', back_populates='route_step')
# def __repr__(self):
# 	return f'step={self.step}'


# class InterToQuest(Base):
# 	__tablename__ = 'interviewers_to_questionnaires'
#
# 	interviewer_id = Column(Integer, ForeignKey('interviewers.id'), primary_key=True)
# 	questionnaire_id = Column(Integer, ForeignKey('questionnaires.id'), primary_key=True)
# 	child = relationship('Questionnaire')


InterToQuest = Table('users_to_questionnaires', Base.metadata,
	Column('users_id', Integer, ForeignKey('users.id')),
	Column('questionnaires_id', Integer, ForeignKey('questionnaires.id'))
)


class User(Base):
	__tablename__ = 'users'

	ADMIN_IDS = [305258161]

	id = Column(Integer, primary_key=True)
	tg_id = Column(Integer, unique=True, nullable=False, primary_key=True)
	chat_id = Column(Integer, unique=False, nullable=False) # todo: should be unique
	first_name = Column(String(64), )
	last_name = Column(String(64), )
	username = Column(String(64), )

	is_interviewer = Column(Boolean, default=True, nullable=False)
	is_admin = Column(Boolean, default=False, nullable=False)

	available_questionnaires = relationship('Questionnaire', secondary=InterToQuest, backref='allowed_users')

	def __repr__(self):
		status = []
		if self.is_admin:
			status.append('Admin')
		if self.is_interviewer:
			status.append('Interviewer')

		d = {
			'first_name': self.first_name,
			'last_name': self.last_name,
			'tg_id': self.tg_id,
			'status': ', '.join(status)
		}
		return '<User({status}) {first_name} {last_name} id: {tg_id}>'.format(**d)


# get_users = lambda: json.load(open(USER_FILE, 'r', encoding='utf-8'))


# user_dict = get_users()


# class User:
# 	def __init__(self, user):
# 		self.existed = False
# 		self.id = str(user.id)
# 		self.first_name = user.first_name
# 		self.last_name = user.last_name
# 		try:
# 			user_dict = get_users()
# 			user_saved = user_dict[self.id]
# 			self.preferred_name = user_saved.get('preferred_name')
# 			self.age = user_saved.get('age')
# 			self.sex = user_saved.get('sex')
# 			self.latitude = user_saved.get('latitude')
# 			self.longitude = user_saved.get('longitude')
# 			self.photos = user_saved.get('photos')
# 			self.existed = True
# 			self.q1 = user_saved.get('q1')
# 			self.q2 = user_saved.get('q2')
# 			self.q3 = user_saved.get('q3')
# 			print('Got user from json')
# 		except KeyError:
# 			self.preferred_name = f'{self.first_name} {self.last_name}'
# 			self.age = None
# 			self.sex = None
# 			self.latitude = None
# 			self.longitude = None
# 			self.q1 = None
# 			self.q2 = None
# 			self.q3 = None
# 			self.photos = []
# 			print('Created new user')
#
# 	# @property
# 	# def serialized(self):
# 	# 	return json.dumps(self.__dict__)
#
# 	def save(self):
# 		# get_users()
# 		user_dict = get_users()
# 		user_dict[self.id] = self.__dict__
# 		json.dump(user_dict, open(USER_FILE, 'w', encoding='utf-8'))
#
# 	def purge(self):
# 		user_dict = get_users()
# 		del user_dict[self.id]
# 		json.dump(user_dict, open(USER_FILE, 'w', encoding='utf-8'))
#
# 	def __repr__(self):
# 		d = self.__dict__.copy()
# 		del d['existed']
# 		lst = []
# 		for k, v in d.items():
# 			if k == 'photos':
# 				v = '[\n\t' + ",\n\t".join(v) + '\n]'
# 			lst.append(f'{k}: {v}')
# 		return '\n'.join(lst)


if __name__ == '__main__':
	s = Session()
	tables = [i[0] for i in s.execute('select distinct tbl_name from sqlite_master')]
	s.close()
	s = Session()
	for table in tables:
		s.execute('drop table {}'.format(table))

	Base.metadata.create_all(engine)
