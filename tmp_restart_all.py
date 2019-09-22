from survey.models import recreate_all, Session, User
from survey.result_table import create_result_table

recreate_all()
me = User(
	tg_id=305258161,
	first_name='A',
	last_name='D',
	is_admin=True
)
s = Session()
s.add(me)
s.commit()

import gluten_shops.survey_script as script

create_result_table(script.questionnaire)
print('READ THIS', 'https://docs.sqlalchemy.org/en/13/orm/extensions/automap.html')
