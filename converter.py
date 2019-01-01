from pydub import AudioSegment
from math import *
import os


def calc_pan(index):
    cos_index = cos(radians(index))
    if cos_index > 0.9:
        cos_index = 0.9
    elif cos_index < -0.9:
        cos_index = -0.9

    return cos_index


def convert_music(directory):
    interval = 0.2 * 1000  # sec
    song = AudioSegment.from_mp3(directory)
    song_inverted = song.invert_phase()
    song.overlay(song_inverted)

    splitted_song_inverted = []
    splitted_song = splitted_song_inverted
    song_start_point = 0

    while song_start_point + interval < len(song):
        splitted_song.append(song[song_start_point:song_start_point + interval])
        song_start_point += interval

    if song_start_point < len(song):
        splitted_song.append(song[song_start_point:])

    ambisonics_song = splitted_song.pop(0)
    pan_index = 0
    for piece in splitted_song:
        pan_index += 5
        piece = piece.pan(calc_pan(pan_index))
        ambisonics_song = ambisonics_song.append(piece, crossfade=interval / 50)

    # lets save it!
    converted_directory = 'music_converted/' + directory
    out_f = open(converted_directory, 'wb')

    ambisonics_song.export(out_f, format='mp3')
    os.remove(directory)

    return converted_directory


# convert_music('Lovely.mp3')
