from survey.models import recreate_all, Session, User

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

import gluten_shops.survey_script