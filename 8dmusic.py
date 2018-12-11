import time
import sys

import requests
import telebot

from converter import convert_music

TOKEN = '742161680:AAEKsvHNB3LKZjvqmKQe4hx7MFdAfwmJHLI'
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def message_start(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, 'convert 8d')


@bot.message_handler(content_types=['audio'])
def message_audio(message):
    performer = message.audio.performer
    title = message.audio.title
    song_name = '{0} - {1}'.format(performer, title)

    file_info = message.audio.file_id

    # convert voice messgae to mp3 file
    mediafile_url = 'https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path)
    media_file_video = requests.get(mediafile_url)

    media_filepath = 'music/{0}.mp3'.format(song_name).encode('utf-8').strip()
    with open(media_filepath, 'wb') as media_filehandler:
        saved_music = media_filehandler.write(media_file_video.content)
        converted_music = convert_music(saved_music)

    bot.send_audio(message.chat.id, open(converted_music, 'wb'))


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



