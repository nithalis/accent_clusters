import logging
import multiprocessing
import os
import sys
import gentle
from pydub import AudioSegment
import json
import requests
import csv

def send_request(audiofile, textfile):

    audio = audiofile + ".mp3"


    params = (
    ('async', 'false'),
    )

    files = {
    'audio': (audio, open(audio, 'rb')),
    'transcript': (textfile, open(textfile, 'rb')),
    }

    print("sending")

    response = requests.post('http://localhost:8765/transcriptions', params=params, files=files)

    #print(response.json())
    return response.json()


def trim_audio(full_audio, start_time, end_time, phone, accent, num):
    # need all times in milliseconds
    print(phone, accent, num)
    audio = AudioSegment.from_mp3(full_audio + '.mp3')
    extract = audio[start_time:end_time]
    #extract.export(str(phone) + "_" + str(accent) + "_" + str(num) + "_" + full_audio + '.wav', format='wav')
    audio_file = full_audio.replace("sample_500/", "")

    extract.export("cut_audio/"+str(phone) + "_" + str(accent) + "_" + str(num) + "_" + audio_file + '.wav', format='wav')

    return extract

def isVowel(letter):
    vowels = ['a', 'e', 'i', 'o', 'u']
    if letter in vowels:
        return True
    else:
        return False


def get_vowel_times(json_file):
    times = []
    for word in json_file['words']:
        if 'phones' in word:
            start_time = word['start']
            for phone in word['phones']:
                curr_phone = phone['phone']
                if isVowel(curr_phone[0]) and "oov" not in curr_phone:
                    time = []
                    time.append(curr_phone)
                    time.append(start_time * 1000)
                    start_time += phone['duration']
                    time.append(start_time * 1000)
                    times.append(time)
                else:
                    start_time += phone['duration']
    return times


def main():

    firstLine = 0

    with open('samples_500.csv', 'r') as samples:
        rd = csv.reader(samples, delimiter=",")
        for sample in rd:
            if firstLine > 0:
                audio_file = sample[1]
                accent = sample[7]
                audio_file = audio_file.replace(".mp3", "").strip()
                with open("transcript.txt", 'w') as temp:
                    temp.write(sample[2])
                temp.close()
                text_file = "transcript.txt"

                # print('aligning', "clips/"+audio_file)
                json_data = send_request("sample_500/"+audio_file, text_file)

                new_times = get_vowel_times(json_data )

                if new_times:
                    count = 0
                    for time in new_times:
                        test = trim_audio("sample_500/"+audio_file, time[1], time[2], time[0], accent, count)
                        count += 1


            firstLine += 1

if __name__ == '__main__':
    main()
