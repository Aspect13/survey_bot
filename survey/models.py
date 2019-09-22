import datetime
import json
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, DateTime, Boolean, UniqueConstraint, \
	Table
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy_utils import ChoiceType

from settings import DB_PATH, USER_FILE

engine = create_engine(f'sqlite:///{DB_PATH}', echo=__name__ == '__main__')
# Session = sessionmaker(bind=engine)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
Base = declarative_base()
AutomapBase = automap_base(Base)


# class Survey(Base):
# 	__tablename__ = 'surveys'
#
# 	id = Column(Integer, primary_key=True)
# 	questionnaire_id = Column(Integer, ForeignKey('questionnaires.id'), nullable=False)
# 	questionnaire = relationship('Questionnaire', back_populates='surveys')


class Questionnaire(Base):
	__tablename__ = 'questionnaires'
	__table_args__ = (UniqueConstraint('name', 'version', name='uc_1'),)

	id = Column(Integer, primary_key=True)
	name = Column(String(64), nullable=False)
	description = Column(String(256), nullable=True)
	version = Column(Integer, nullable=False)
	is_active = Column(Boolean, nullable=False, default=False)

	# results_table = relationship('sqlite_master', back_populates='questionnaire')
	results_table_name = Column(String(64), nullable=True)

	# questions = relationship('Question', back_populates='questionnaire', cascade='all, delete, delete-orphan',
	#                          order_by='Question.id')
	questions = relationship('Question', backref='questionnaire', cascade='all, delete, delete-orphan',
	                         order_by='Question.id')

	# created_by = relationship('User', back_populates='created_questionnaires')
	# created_by = relationship('User', backref='created_questionnaires')
	created_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
	# surveys = relationship('Survey', back_populates='questionnaire')

	def __repr__(self):
		return f'<Questionnaire {self.name} v{self.version}  {"(active)" if self.is_active else "(not active)"}>'


class QuestionTypes:
	info = 'info'
	categorical = 'categorical'
	photo = 'photo'
	location = 'location'
	text = 'text'
	sticker = 'sticker'
	datetime = 'datetime'
	timestamp = 'timestamp'
	integer = 'integer'

	def __iter__(self):
		return ((i, i) for i in filter(lambda attr: not attr.startswith('__'), QuestionTypes.__dict__))

	def __getitem__(self, item, default=None):
		return self.__getattribute__(item)



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
	type = Column(ChoiceType(QuestionTypes()))
	save_in_survey = Column(Boolean, nullable=False, default=True)
	step = Column(Integer, )

	# categories = relationship('Category', back_populates='question', cascade='all, delete, delete-orphan', )
	categories = relationship('Category', backref='question', cascade='all, delete, delete-orphan', )

	# route_step = relationship('Route', back_populates='question', uselist=False, cascade='all, delete, delete-orphan')

	questionnaire_id = Column(Integer, ForeignKey('questionnaires.id'), nullable=False)
	# questionnaire = relationship('Questionnaire', back_populates='questions')


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
		return f'<Question code={self.code} text={self.text[:10]}... {self.step}>'


class Category(Base):
	__tablename__ = 'categories'
	__table_args__ = (UniqueConstraint('question_id', 'code', name='uc_1'),)

	id = Column(Integer, primary_key=True)
	text = Column(String(256), nullable=False)
	code = Column(String(64), nullable=False)

	question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
	# question = relationship('Question', back_populates='categories')

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
	Column('questionnaires_id', Integer, ForeignKey('questionnaires.id')),
)

AdminToQuest = Table('admins_to_questionnaires', Base.metadata,
	Column('users_id', Integer, ForeignKey('users.id')),
	Column('questionnaires_id', Integer, ForeignKey('questionnaires.id')),
)


class User(Base):
	__tablename__ = 'users'

	ADMIN_IDS = [305258161]

	id = Column(Integer, primary_key=True)
	tg_id = Column(Integer, unique=True, nullable=False,)
	# chat_id = Column(Integer, unique=False, nullable=False) # todo: should be unique
	first_name = Column(String(64), )
	last_name = Column(String(64), )
	username = Column(String(64), )
	date_joined = Column(DateTime, nullable=False, default=datetime.datetime.now())

	is_interviewer = Column(Boolean, default=True, nullable=False)
	is_admin = Column(Boolean, default=False, nullable=False)

	available_questionnaires = relationship('Questionnaire', secondary=InterToQuest, backref='project_users')
	admin_of_projects = relationship('Questionnaire', secondary=AdminToQuest, backref='project_admins')

	# created_questionnaires = relationship('Questionnaire', back_populates='created_by')
	created_questionnaires = relationship('Questionnaire', backref='created_by')

	@property
	def is_root(self):
		return self.tg_id == 305258161

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


def recreate_all(session=None):
	if not session:
		session = Session()
	tables = [i[0] for i in session.execute('select distinct tbl_name from sqlite_master')]
	session.close()
	session = Session()
	for table in tables:
		session.execute('drop table if exists {}'.format(table))
	# Base.prepare()
	Base.metadata.create_all(engine)


if __name__ == '__main__':
	# recreate_all()
	print('Use tmp_restart_all.py')
