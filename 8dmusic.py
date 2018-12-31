import time
import sys
import os

import requests
import telebot

from converter import convert_music

TOKEN = '742161680:AAHXvLIHicCaEvpZwqIVzxB2Nr7Hs0MCiAY'
bot = telebot.TeleBot(TOKEN)


def lang(message):
    if (message.from_user.language_code is not None and
            'ru' in message.from_user.language_code):
        return 'ru'
    return 'en'


string = {
    'ru': {'start': 'С помощью этого бота вы сможете сконвертировать песню на 8D',
           'wait': 'Please wait, your music is converting'},
    'en': {'start': 'By using this bot you can convert your music to 8D',
           'wait': 'Пожалуйста, подождите, ваша музыка конвертируется'}
}


@bot.message_handler(commands=['start'])
def message_start(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, string[lang(message)]['start'])


@bot.message_handler(content_types=['audio'])
def message_audio(message):
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



