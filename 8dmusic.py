import re
import time
import sys
import os

import requests
import telebot

from models import *
from converter import convert_music

import sentry_sdk
sentry_sdk.init("https://d370e00b0de240b3be67867f140351d8@sentry.io/1307044")

TOKEN = '640619242:AAG7lD0H8xO0_3krqmJZuiFC69-68IW66Cw'
bot = telebot.TeleBot(TOKEN)
TG_ADMIN_ID = 713731388

ref_link = 'https://telegram.me/{}?start={}'


def lang(message):
    if (message.from_user.language_code is not None and
            'ru' in message.from_user.language_code):
        return 'ru'
    return 'en'


string = {
    'ru': {'start': 'By using this bot you can convert your music to 8D format. Just send me a music',
           'wait': 'Please wait, your music is converting. It may take about 1 minute',
           'ref': 'For using this bot, please invite 1 friend by this link 👇',
           'count': 'Total invited: {}',
           'link': 'Your referal link👇\n'},
    'en': {'start': 'С помощью этого бота вы сможете сконвертировать песню на 8D формат. Сперва отправь мне песню',
           'wait': 'Пожалуйста, подождите, ваша музыка конвертируется. Это может занять около 1 минуты',
           'ref': 'Для использования этого бота, пригластите одного друга, отправив эту ссылку 👇',
           'count': 'Всего приглашено: {}',
           'link': 'Ваша реферальная ссылка👇\n'}
}


@bot.message_handler(commands=['get_my_link'])
def get_my_ref(message):
    # получаем username нашего бота и отпрявляем ссылку
    bot_name = bot.get_me().username
    bot.send_message(message.chat.id, string[lang(message)]['link'] + ref_link.format(bot_name, message.chat.id),
                     disable_web_page_preview=True)


@bot.message_handler(commands=['ref_count'])
def get_ref_count(message):
    # запрашиваем кол-во рефералов пользователя и отправляем ему
    count = Users.get_ref_count(message.chat.id)
    bot.send_message(message.chat.id, string[lang(message)]['count'].format(count))


@bot.message_handler(commands=['start'])
def message_start(message):
    bot.send_chat_action(message.chat.id, 'typing')

    user_id = message.chat.id
    splited = message.text.split()
    # проверяем наличие пользователя в базе данных
    if not Users.user_exists(user_id):
        # если его нет -- создаём
        Users.create_user(user_id)
        # проверяем перешел ли пользователь по реферальной ссылке
        if len(splited) == 2:
            # увеличиваем счетчик тому кто пригласил
            Users.increase_ref_count(splited[1])

    bot.send_message(message.chat.id, string[lang(message)]['start'])

    user_message = '{0}'.format(message.from_user.id)
    if user_message in open('users_id.txt').read():
        pass
    else:
        user_file = open('users_id.txt', 'a')
        user_file.write('{0}.'.format(message.from_user.id))
        user_file.close()

    if message.from_user.id == TG_ADMIN_ID:
        bot.send_message(TG_ADMIN_ID, '/get_users - Получить статистику пользователей\n'
                                      '/check_users - Получить количество пользователей, которые удалили бота\n'
                                      '/delete_users_id - Получить список id пользователей, которые удалили бота')


@bot.message_handler(content_types=['text'])
def admin_message(message):
    if message.from_user.id == TG_ADMIN_ID:
        if message.text == '/get_users':
            users = len(re.findall(r"[\n']+", open('users_id.txt').read()))
            deleted_user = len(re.findall(r"[\n']+", open('delete_user.txt').read()))
            bot.send_message(TG_ADMIN_ID, 'Всего пользователей: {0}\nЗаблокировали бота: {1}'
                             .format(users + 1, deleted_user))

        if message.text == '/check_users':
            users_id = open('users_id.txt')
            i = 0
            for user_id in users_id.read().split('\n'):
                try:
                    bot.send_chat_action(user_id, 'typing')
                except Exception:
                    i = i + 1
                    delete_user = open('delete_user.txt', 'a')
                    delete_user.write('{0}.'.format(user_id))

            bot.send_message(TG_ADMIN_ID, 'Удалили всего: {} пользователей'.format(i))

        if message.text == '/delete_users_id':
            try:
                deleted_user = len(open('delete_user.txt').read().split('.'))
                i = 0
                for users in range(deleted_user - 1):
                    i = i + 1
                    users += open('delete_user.txt').read().split('.')[i]
                    bot.send_message(TG_ADMIN_ID, 'Список id пользователей, удаливших вашего бота:\n{}'.format(users))
            except Exception:
                bot.send_message(TG_ADMIN_ID, 'Никто не удалил вашего бота')


@bot.message_handler(content_types=['audio'])
def message_audio(message):
    count = Users.get_ref_count(message.chat.id)
    if count >= 1:
        waiting = bot.send_message(message.chat.id, string[lang(message)]['wait'])
        performer = message.audio.performer + ' 8D'
        title = message.audio.title

        file_id = message.audio.file_id

        # convert voice messgae to mp3 file
        mediafile_info = bot.get_file(file_id)
        mediafile_url = 'https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, mediafile_info.file_path)
        media_file_video = requests.get(mediafile_url)

        media_filepath = '{0}.mp3'.format(message.from_user.id)
        with open(media_filepath, 'wb') as media_filehandler:
            media_filehandler.write(media_file_video.content)

        converted_music = convert_music(media_filepath)

        bot.send_chat_action(message.chat.id, 'record_audio')
        bot.send_audio(message.chat.id, open('music_converted/{0}.mp3'.format(message.from_user.id), 'rb'),
                       performer=performer, title=title)

        bot.delete_message(message.chat.id, waiting.message_id)

        os.remove(str(converted_music))
    else:
        bot_name = bot.get_me().username
        bot.send_message(message.chat.id, string[lang(message)]['ref']+'\n'+ref_link.format(bot_name, message.chat.id),
                         disable_web_page_preview=True)


def main_loop():
    bot.polling(True)
    while 1:
        time.sleep(1)


if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print(sys.stderr, '\nExiting by user request.\n')
        sys.exit(0)
