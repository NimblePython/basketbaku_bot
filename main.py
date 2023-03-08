import time, threading, schedule
import telebot, wikipedia, re
from telebot import types

# Устанавливаем русский язык в Wikipedia
wikipedia.set_lang("ru")
# Создаем объект бота
bot = telebot.TeleBot('5735237236:AAGNyBBM5NJloqjETQMqjCX6qeTIGDXks2g')


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup2 = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('👋 Поздороваться')
    itm1 = types.InlineKeyboardButton(text='О нас', callback_data=1)
    itm2 = types.InlineKeyboardButton(text='Адрес зала', callback_data=2)
    itm3 = types.InlineKeyboardButton(text='Условия', callback_data=3)
    itm4 = types.InlineKeyboardButton(text='Расписание занятий', callback_data=4)
    markup.add(itm1, itm2, itm3, itm4)
    markup2.add(btn1)
    bot.send_message(message.chat.id,
                     '👋 Привет! Можешь задать интересующий тебя вопрос про баскетбол или воспользоваться '
                     'кнопками-подсказаками',
                     reply_markup=markup)
    # bot.reply_to(message, 'Hi! Use /set <seconds> to set a timer')


@bot.message_handler(commands=['set'])
def set_timer(message):
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        sec = int(args[1])
        schedule.every(sec).seconds.do(beep, message.chat.id).tag(message.chat.id)
    else:
        bot.reply_to(message, 'Usage: /set <seconds>')


@bot.message_handler(commands=['unset'])
def unset_timer(message):
    schedule.clear(message.chat.id)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '👋 Поздороваться':
        #markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        #btn1 = types.KeyboardButton('Напишите термин из баскетбола, я помогу найти информацию об этом')
        #markup.add(btn1)
        bot.send_message(message.chat.id,
                         '❓ Можешь задать интересующий вопрос про баскетбол или воспользоваться кнопками-подсказаками')
    elif message.text == 'Адрес':
        bot.send_message(message.from_user.id,
                         'Вы пишете первый пост, его проверяют модераторы, и, если всё хорошо, отправляют в основную '
                         'ленту Хабра, где он набирает просмотры, комментарии и рейтинг. В дальнейшем премодерация уже '
                         'не понадобится. Если с постом что-то не так, вас попросят его доработать.\n \nПолный текст '
                         'можно прочитать по ' + '[ссылке](https://habr.com/ru/sandbox/start/)',
                         parse_mode='Markdown')
    elif message.text == 'Расписание':
        bot.send_message(message.from_user.id,
                         'Прочитать правила сайта вы можете по ' + '[ссылке](https://habr.com/ru/docs/help/rules/)',
                         parse_mode='Markdown')
    elif message.text == 'Условия':
        bot.send_message(message.from_user.id,
                         'Подробно про советы по оформлению публикаций прочитать по ' +
                         '[ссылке](https://habr.com/ru/docs/companies/design/)',
                         parse_mode='Markdown')
    else:
        bot.send_message(message.from_user.id, getwiki(message.text))


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id, text='')
    answer = ''
    if call.data == '1':
        answer = 'Ты находишься в группе любителей баскетбола из Баку. Все мы неравнодушны к этому виду ' \
                 'спорта и всегда рады новым друзьям, кто также разделяет эту любовь к Его величеству Баскетболу. ' \
                 'Наша группа состит из абсолютно разных возрастных категорий в диапазоне от 20 и до 40+ лет, поэтому ' \
                 'ты обязательно найдешь у нас игрока с которым ты захочешь сыграть в одной команде или же своего ' \
                 'достойного антогониста =) Наш уровень игры - превосходно разнообразен. ' \
                 'Приходи и стань частью нашей команды =)'
    if call.data == '2':
        answer = 'Мы играем в спортивном зале школы № 258 по адресу: ул. Академика Гасана Алиева, д. 39'
        map_png = open(r'map.png', 'rb')
        bot.send_photo(call.message.chat.id, map_png)
    if call.data == '3':
        answer = 'Абонентская плата в месяц:\n4 посещения в месяц - 40 манат\n' \
                 '8 посещений в месяц - 80 манат' \
                 '\n\nПропущенные посещения на следующий месяц не переносятся.' \
                 '\n\nЕсли ты не уверен и хочешь присмотреться, то первое ознакомительное посещение будет бесплатным =)'
    if call.data == '4':
        answer = 'Игры проходят два раза в неделю:\n\n' \
                 '======  ВТОРНИК в 20-00  ======\n\n' \
                 '======  ЧЕТВЕРГ в 20-00   ======'
    bot.send_message(call.message.chat.id, answer)
    # Убираем клавиатуру
    # bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)


# Чистим текст статьи в Wikipedia и ограничиваем его тысячей символов
def getwiki(s):
    try:
        ny = wikipedia.page(s)
        # Получаем первую тысячу символов
        wikitext = ny.content[:1000]
        # Разделяем по точкам
        wikimas=wikitext.split('.')
        # Отбрасываем всЕ после последней точки
        wikimas = wikimas[:-1]
        # Создаем пустую переменную для текста
        wikitext2 = ''
        # Проходимся по строкам, где нет знаков «равно» (то есть все, кроме заголовков)
        for x in wikimas:
            if not('==' in x):
                # Если в строке осталось больше трех символов, добавляем ее к нашей переменной и возвращаем утерянные при разделении строк точки на место
                if len((x.strip())) > 3:
                   wikitext2 = wikitext2 + x + '.'
            else:
                break
        # При помощи регулярных выражений убираем разметку
        wikitext2 = re.sub('\([^()]*\)', '', wikitext2)
        wikitext2 = re.sub('\([^()]*\)', '', wikitext2)
        wikitext2 = re.sub('\{[^\{\}]*\}', '', wikitext2)
        return wikitext2
    # Обрабатываем исключение, которое мог вернуть модуль wikipedia при запросе
    except Exception as e:
        return 'В источнике нет информации об этом'


def beep(chat_id) -> None:
    """Send the beep message"""
    bot.send_message(chat_id, text='Время вышло!')


if __name__ == '__main__':
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    while True:
        schedule.run_pending()
        time.sleep(1)
# bot.polling(none_stop=True, interval=0)

