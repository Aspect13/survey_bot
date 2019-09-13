from survey.gluten_shops.settings import save
from survey.models import Question, Category, location, photo, categorical, info


#
#
# Here go questions:
#
#
q = Question()
q.code = 'q1'
q.type = info
q.text = 'Привет, исследователь! Надеюсь, твой гаджет хорошо заряжен, и в нем достаточно свободной памяти. Тебе предстоит сделать много фоток и нагулять хороший аппетит😄     Будь внимателен! Посмотри дважды, прежде чем ответить или сделать фото👀    Если сомневаешься, все равно фоткай. Да пребудет с тобой Сила Киноа!🙌'
save()

q = Question()
q.code = 'q2'
q.type = location
q.text = 'Нажми на кнопку, чтобы отправить геолокацию, и я узнаю, в каком ты сейчас магазине'
cats = [Category(text='Отправить местоположение'), ]
q.categories = cats
save()

q = Question()
q.code = 'q3'
q.type = photo
q.text = 'А еще сфоткай, пожалуйста, как выглядит вход в магазин с улицы'
save()

q = Question()
q.code = 'q4'
q.type = photo
q.text = 'Ты уже внутри? Сделай фото прикассовой зоны, я посмотрю чисто и красиво ли там'
save()

q = Question()
q.code = 'q5'
q.type = categorical
q.text = 'Принято! Теперь иди в отдел бакалеи. Найди стеллаж с макаронами/пастой   Посмотри есть ли там продукты без глютена? '
cats = [Category(text='Да'), Category(text='Нет'), ]
q.categories = cats
save()

