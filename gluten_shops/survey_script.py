from emoji import emojize

from survey.survey_builder import _get_questionnaire, _save
from survey.models import Question, QuestionTypes as types, Session, Category, User

QUESTIONNAIRE_VERSION = 1
QUESTIONNAIRE_NAME = 'gluten_shops'
QUESTIONNAIRE_DESCRIPTION = 'Исследование магазинов с безглютеновой продукцией'
ROUTE_STEP = 1
ALLOW_OVERWRITE = False


def get_questionnaire(session=None, **kwargs):
	return _get_questionnaire(QUESTIONNAIRE_NAME, QUESTIONNAIRE_VERSION, QUESTIONNAIRE_DESCRIPTION, session=session, **kwargs)


session = Session()
me = session.query(User).filter(User.tg_id == 305258161).first()
questionnaire = get_questionnaire(session=session, created_by=me)


def save(q):
	global ROUTE_STEP
	saved = _save(q, questionnaire, step=ROUTE_STEP, session=session, allow_overwrite=ALLOW_OVERWRITE)
	ROUTE_STEP += 1
	return saved



shops = [
	{'name': 'ГУМ', 'address': 'Красная площадь, 3, Москва, 109012', 'latitude': 55.7546942, 'longitude': 37.6214334},
]

#
#
# Here go questions:
#
#

yes_no_cats = lambda: [
    Category(text=emojize('Да :simple_smile:')),
    Category(text=emojize('Нет :pensive:'))
]

three_scale_cats = lambda: [
    Category(text=emojize('Да, все четко! :thumbsup:')),
    Category(text=emojize('На троечку, порядка не хватает :grin:')),
    Category(text=emojize('Все плохо, хочется убежать :scream:'))
]


q = Question()
q.code = 'q1'
q.type = types.info
q.text = emojize(
	'Привет, исследователь! Надеюсь, твой гаджет хорошо заряжен, и в нем достаточно свободной памяти.' +
	'Тебе предстоит сделать много фоток и нагулять хороший аппетит :smile:\n' +
	'Будь внимателен! Посмотри дважды, прежде чем ответить или сделать фото :eyes:\n' +
	'Если сомневаешься, все равно фоткай. Да пребудет с тобой Сила Киноа! :raised_hands:'
)
save(q)

q = Question()
q.code = 'q2'
q.type = types.location
q.text = emojize('Нажми на кнопку, чтобы отправить геолокацию, и я узнаю, в каком ты сейчас магазине :round_pushpin:')
cats = [Category(text='Отправить местоположение'), ]
q.categories = cats
save(q)


q = Question()
q.code = 'shops'
q.type = types.categorical
q.text = 'Вот найденные магазины:'
cats = [Category(text=f'{i["name"]} ({i["address"]})') for i in shops]
q.categories = cats
save(q)


q = Question()
q.code = 'q3'
q.type = types.photo
q.text = emojize('А еще сфоткай, пожалуйста, как выглядит вход в магазин с улицы :camera:')
save(q)

q = Question()
q.code = 'q4'
q.type = types.photo
q.text = emojize('Ты уже внутри? Сделай фото прикассовой зоны, я посмотрю чисто и красиво ли там :camera:')
save(q)

q = Question()
q.code = 'q5'
q.type = types.categorical
q.text = emojize('Принято! Теперь иди в отдел бакалеи. Найди стеллаж с макаронами/пастой :ramen:\nПосмотри есть ли там продукты без глютена?')
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q6'
q.type = types.photo
q.text = emojize('Покажи мне тоже эти стеллажи :camera:')
save(q)

q = Question()
q.code = 'q7'
q.type = types.categorical
q.text = 'А есть ли на полках макароны/паста не из пшеницы? Например, из рисовой или гречишной муки'
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q8'
q.type = types.photo
q.text = emojize('Покажи мне тоже эти стеллажи :camera:')
save(q)

q = Question()
q.code = 'q9'
q.type = types.text
q.text = emojize('А что там рядом с макаронами? Напиши, какие полки расположены слева?:point_left:')
save(q)

q = Question()
q.code = 'q10'
q.type = types.text
q.text = emojize('А какие справа? :point_right:')
save(q)

q = Question()
q.code = 'q11'
q.type = types.text
q.text = emojize('А что напротив? :point_up:')
save(q)

q = Question()
q.code = 'q12'
q.type = types.categorical
q.text = 'Класс! А теперь расскажи, нравится ли тебе этот отдел? Полки хорошо организованы, нет беспорядка, продукты красиво расставлены?'
cats = three_scale_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q13'
q.type = types.photo
q.text = emojize('Переходи в отдел круп. Мне нужны все товары, в которых есть киноа. Как найдешь, фоткай :camera:')
save(q)

q = Question()
q.code = 'q14'
q.type = types.text
q.text = emojize('А что там рядом с крупами? Напиши, какие полки расположены слева?:point_left:')
save(q)

q = Question()
q.code = 'q15'
q.type = types.text
q.text = emojize('А какие справа? :point_right:')
save(q)

q = Question()
q.code = 'q16'
q.type = types.text
q.text = emojize('А что напротив? :point_up:')
save(q)

q = Question()
q.code = 'q17'
q.type = types.categorical
q.text = 'Класс! А теперь расскажи, нравится ли тебе этот отдел? Полки хорошо организованы, нет беспорядка, продукты красиво расставлены?'
cats = three_scale_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q18'
q.type = types.photo
q.text = emojize('Теперь найди муку и смеси для выпечки! Сфоткай все полки с мукой и смесями какие есть в магазине :camera:')
save(q)

q = Question()
q.code = 'q19'
q.type = types.categorical
q.text = 'А давай конкретнее. Есть ли мука не из пшеницы?'
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q20'
q.type = types.photo
q.text = emojize('Если есть, то покажи какая! :camera:')
save(q)

q = Question()
q.code = 'q21'
q.type = types.photo
q.text = emojize('На смеси для выпечки БЕЗ ГЛЮТЕНА тоже очень хочется посмотреть :camera:')
save(q)

q = Question()
q.code = 'q22'
q.type = types.text
q.text = emojize('А что там рядом с этим отделом? Напиши, какие полки расположены слева?:point_left:')
save(q)

q = Question()
q.code = 'q23'
q.type = types.text
q.text = emojize('А какие справа? :point_right:')
save(q)

q = Question()
q.code = 'q24'
q.type = types.text
q.text = emojize('А что напротив? :point_up:')
save(q)

q = Question()
q.code = 'q25'
q.type = types.categorical
q.text = 'Класс! А теперь расскажи, нравится ли тебе этот отдел? Полки хорошо организованы, нет беспорядка, продукты красиво расставлены?'
cats = three_scale_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q26'
q.type = types.categorical
q.text = 'Двигаемся дальше! Переходим к сладенькому – отдел печений. Есть ли там продукты без глютена?'
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q27'
q.type = types.photo
q.text = emojize('А покажи мне эти стеллажи :camera:')
save(q)

q = Question()
q.code = 'q28'
q.type = types.photo
q.text = emojize('А давай конкретнее. Сфоткай все группы сладостей, в которых НЕТ ГЛЮТЕНА! Например, печенья, вафли, галеты, батончики, крекеры :camera:')
save(q)

q = Question()
q.code = 'q29'
q.type = types.categorical
q.text = emojize('Как аппетитно!:heart_eyes: А есть на полках несладкие печенья? Например, соленые крекеры')
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q30'
q.type = types.photo
q.text = emojize('Покажи мне их тоже! Очень любопытно :camera:')
save(q)

q = Question()
q.code = 'q31'
q.type = types.text
q.text = emojize('А что там рядом с этим отделом? Напиши, какие полки расположены слева?:point_left:')
save(q)

q = Question()
q.code = 'q32'
q.type = types.text
q.text = emojize('А какие справа? :point_right:')
save(q)

q = Question()
q.code = 'q33'
q.type = types.text
q.text = emojize('А что напротив? :point_up:')
save(q)

q = Question()
q.code = 'q34'
q.type = types.categorical
q.text = 'Класс! А теперь расскажи, нравится ли тебе этот отдел? Полки хорошо организованы, нет беспорядка, продукты красиво расставлены?'
cats = three_scale_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q35'
q.type = types.categorical
q.text = 'Следующая остановка – отдел готовых завтраков. Есть ли там продукты без глютена?'
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q36'
q.type = types.photo
q.text = emojize('А покажи мне эти стеллажи :camera:')
save(q)

q = Question()
q.code = 'q37'
q.type = types.photo
q.text = emojize('Давай конкретнее. Сфоткай все товары, в которых НЕТ ГЛЮТЕНА! Например, готовые каши, мюсли, батончики, хлебцы, снеки :camera:')
save(q)

q = Question()
q.code = 'q38'
q.type = types.text
q.text = emojize('А что там рядом с этим отделом? Напиши, какие полки расположены слева?:point_left:')
save(q)

q = Question()
q.code = 'q39'
q.type = types.text
q.text = emojize('А какие справа? :point_right:')
save(q)

q = Question()
q.code = 'q40'
q.type = types.text
q.text = emojize('А что напротив? :point_up:')
save(q)

q = Question()
q.code = 'q41'
q.type = types.categorical
q.text = 'Класс! А теперь расскажи, нравится ли тебе этот отдел? Полки хорошо организованы, нет беспорядка, продукты красиво расставлены?'
cats = three_scale_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q42'
q.type = types.categorical
q.text = emojize('Надеюсь, ты не сильно проголодался, а охранник еще не начал подозрительно смотреть на тебя :yum:  Финал близко!\nПосмотри, есть ли в магазине стеллажи с диетической продукцией? Часто на них расположены товары для диабетиков. :herb:')
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q43'
q.type = types.photo
q.text = emojize('А покажи мне эти стеллажи :camera:')
save(q)

q = Question()
q.code = 'q44'
q.type = types.categorical
q.text = 'Есть ли там безглютеновые товары?'
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q45'
q.type = types.categorical
q.text = 'Стеллажи с диетической продукцией расположены близко ко входу?'
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q46'
q.type = types.categorical
q.text = 'А отдел молочных продуктов близко?'
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q47'
q.type = types.categorical
q.text = 'Стеллажи с диетической продукцией расположены глубоко внутри магазина?'
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q48'
q.type = types.categorical
q.text = 'Ни один покупатель не сможет пройти мимо стеллажей с диетической продукцией?'
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q49'
q.type = types.categorical
q.text = 'Стеллажи с диетической продукцией хорошо освещены и товары на них красиво расставлены?'
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q50'
q.type = types.categorical
q.text = emojize('А теперь посмотри, есть ли в магазине стеллажи с органической продукцией? :green_apple: :tangerine:')
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q51'
q.type = types.photo
q.text = emojize('А покажи мне эти стеллажи :camera:')
save(q)

q = Question()
q.code = 'q52'
q.type = types.categorical
q.text = 'Есть ли там безглютеновые товары?'
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q53'
q.type = types.categorical
q.text = 'Органика расположена близко ко входу?'
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q54'
q.type = types.categorical
q.text = 'А отдел молочных продуктов близко?'
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q55'
q.type = types.categorical
q.text = 'Стеллажи с органикой расположены глубоко внутри магазина?'
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q56'
q.type = types.categorical
q.text = 'Ни один покупатель не сможет пройти мимо органики?'
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q57'
q.type = types.categorical
q.text = 'Стеллажи с органикой хорошо освещены и товары на них красиво расставлены?'
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q58'
q.type = types.categorical
q.text = emojize('А теперь посмотри, есть ли в магазине стеллажи с безглютеновой продукцией? А что, а вдруг?! :grinning:')
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q59'
q.type = types.photo
q.text = emojize('А покажи мне эти стеллажи :camera:')
save(q)

q = Question()
q.code = 'q60'
q.type = types.categorical
q.text = 'Стеллажи с безглютеном расположены близко ко входу?'
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q61'
q.type = types.categorical
q.text = 'А отдел молочных продуктов близко?'
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q62'
q.type = types.categorical
q.text = 'Стеллажи с безглютеном расположены глубоко внутри магазина?'
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q63'
q.type = types.categorical
q.text = 'Ни один покупатель не сможет пройти мимо стеллажей с безглютеном?'
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q64'
q.type = types.categorical
q.text = 'Стеллажи с безглютеном хорошо освещены и товары на них красиво расставлены?'
cats = yes_no_cats()
q.categories = cats
save(q)

q = Question()
q.code = 'q65'
q.type = types.info
q.text = emojize('Поздравляю! Уровень пройден :collision: Ты нереальный красавчик! :sunglasses:')
save(q)

q = Question()
q.code = 'q66'
q.type = types.info
q.text = emojize('Если бы я был человеком, то хотел бы иметь такого друга как ты! До встречи в новом магазине! :wink:')
save(q)
