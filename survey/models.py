import json
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, DateTime, Date, Boolean, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy_utils import ChoiceType

from settings import DB_PATH, USER_FILE

engine = create_engine(f'sqlite:///{DB_PATH}', echo=__name__ == '__main__')
# Session = sessionmaker(bind=engine)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
Base = declarative_base()


# types
info = 'info'
categorical = 'categorical'
photo = 'photo'
location = 'location'
text = 'text'


class Survey(Base):
	__tablename__ = 'surveys'

	id = Column(Integer, primary_key=True)
	questionnaire_id = Column(Integer, ForeignKey('questionnaires.id'), nullable=False)
	questionnaire = relationship('Questionnaire', back_populates='surveys')


class Questionnaire(Base):
	__tablename__ = 'questionnaires'
	__table_args__ = (UniqueConstraint('version', 'name', name='uc_1'), )

	id = Column(Integer, primary_key=True)
	name = Column(String(64), nullable=False)
	description = Column(String(256), nullable=True)
	version = Column(Integer, nullable=False)
	is_available = Column(Boolean, nullable=False, default=False)

	questions = relationship('Question', back_populates='questionnaire', cascade='all, delete, delete-orphan', order_by='Question.id')
	surveys = relationship('Survey', back_populates='questionnaire')


class Question(Base):
	__tablename__ = 'questions'

	TYPES = [
		(info, info),
		(categorical, categorical),
		(photo, photo),
		(location, location),
		(text, text),
	]

	id = Column(Integer, primary_key=True)
	code = Column(String(64), nullable=False, unique=True)
	text = Column(String(512), nullable=False, unique=True)
	type = Column(ChoiceType(TYPES))
	save_in_survey = Column(Boolean, nullable=False, default=True)

	categories = relationship('Category', back_populates='question', cascade='all, delete, delete-orphan')

	route_step = relationship('Route', back_populates='question', uselist=False, cascade='all, delete, delete-orphan')

	questionnaire_id = Column(Integer, ForeignKey('questionnaires.id'), nullable=False)
	questionnaire = relationship('Questionnaire', back_populates='questions')

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


class Route(Base):
	__tablename__ = 'routes'
	__table_args__ = (UniqueConstraint('version', 'step', name='uc_1'), )

	id = Column(Integer, primary_key=True)
	version = Column(Integer, nullable=False)
	step = Column(Integer, nullable=False)
	question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
	question = relationship('Question', back_populates='route_step')

	def __repr__(self):
		return f'step={self.step}'












get_users = lambda: json.load(open(USER_FILE, 'r', encoding='utf-8'))
# user_dict = get_users()


class User:
	def __init__(self, user):
		self.existed = False
		self.id = str(user.id)
		self.first_name = user.first_name
		self.last_name = user.last_name
		try:
			user_dict = get_users()
			user_saved = user_dict[self.id]
			self.preferred_name = user_saved.get('preferred_name')
			self.age = user_saved.get('age')
			self.sex = user_saved.get('sex')
			self.latitude = user_saved.get('latitude')
			self.longitude = user_saved.get('longitude')
			self.photos = user_saved.get('photos')
			self.existed = True
			self.q1 = user_saved.get('q1')
			self.q2 = user_saved.get('q2')
			self.q3 = user_saved.get('q3')
			print('Got user from json')
		except KeyError:
			self.preferred_name = f'{self.first_name} {self.last_name}'
			self.age = None
			self.sex = None
			self.latitude = None
			self.longitude = None
			self.q1 = None
			self.q2 = None
			self.q3 = None
			self.photos = []
			print('Created new user')

	# @property
	# def serialized(self):
	# 	return json.dumps(self.__dict__)

	def save(self):
		# get_users()
		user_dict = get_users()
		user_dict[self.id] = self.__dict__
		json.dump(user_dict, open(USER_FILE, 'w', encoding='utf-8'))

	def purge(self):
		user_dict = get_users()
		del user_dict[self.id]
		json.dump(user_dict, open(USER_FILE, 'w', encoding='utf-8'))

	def __repr__(self):
		d = self.__dict__.copy()
		del d['existed']
		lst = []
		for k, v in d.items():
			if k == 'photos':
				v = '[\n\t' + ",\n\t".join(v) + '\n]'
			lst.append(f'{k}: {v}')
		return '\n'.join(lst)


if __name__ == '__main__':
	s = Session()
	try:
		s.execute('drop table categories')
		s.execute('drop table routes')
		s.execute('drop table questions')
		s.execute('drop table surveys')
		s.execute('drop table questionnaires')
	except:
		pass

	Base.metadata.create_all(engine)

