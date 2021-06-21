import logging
import multiprocessing
import os
import sys
import gentle
from pydub import AudioSegment
import json
import requests
import csv

# figure out damage control if audio does not align
def align(audiofile_name, txtfile):

    nthreads = multiprocessing.cpu_count()
    conservative=False
    disfluency=False

    audiofile = audiofile_name + ".mp3"

    disfluencies = set(['uh', 'um'])

    def on_progress(p):
        for k,v in p.items():
            logging.debug("%s: %s" % (k, v))

    with open(txtfile, encoding="utf-8") as fh:
        transcript = fh.read()

    resources = gentle.Resources()
    logging.info("converting audio to 8K sampled wav")

    with gentle.resampled(audiofile) as wavfile:
        logging.info("starting alignment")
        aligner = gentle.ForcedAligner(resources, transcript, nthreads=nthreads, disfluency=disfluency, conservative=conservative, disfluencies=disfluencies)
        result = aligner.transcribe(wavfile, progress_cb=on_progress, logging=logging)

    fh = open(audiofile_name + ".txt", 'w', encoding="utf-8")
    fh.write(result.to_json(indent=2))

    return result.to_json(indent=2)

######################################################################################################################################

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

######################################################################################################################################


def trim_audio(full_audio, start_time, end_time, phone, accent, num):
    # need all times in milliseconds
    print(phone, accent, num)
    audio = AudioSegment.from_mp3(full_audio + '.mp3')
    extract = audio[start_time:end_time]
    #extract.export(str(phone) + "_" + str(accent) + "_" + str(num) + "_" + full_audio + '.wav', format='wav')
    audio_file = full_audio.replace("data/", "")

    extract.export(str(phone) + "_" + str(accent) + "_" + str(num) + "_" + audio_file + '.wav', format='wav')

    return extract

######################################################################################################################################


def extract_triphones(json_file):
    triphones = []
    words = []
    for word in json_file['words']:
        words.append(word['word'])
        if 'phones' in word:
            if len(word['phones']) >= 3:
                phones = word['phones']
                for phone in range(len(phones) - 2):
                    tri = phones[phone]['phone']
                    tri += (" " + phones[phone + 1]['phone'])
                    tri += (" " + phones[phone + 2]['phone'])
                    triphones.append(tri)
    return triphones, words

######################################################################################################################################


def get_times(triphone, json_file):
    times = []
    for word in json_file['words']:
        if 'phones' in word:
            if len(word['phones']) >= 3:
                phones = word['phones']
                for phone in range(len(phones) - 2):
                    tri = phones[phone]['phone']
                    tri += (" " + phones[phone + 1]['phone'])
                    tri += (" " + phones[phone + 2]['phone'])
                    if tri == triphone:
                        print(word['word'])
                        time = []
                        start_time = word['start']
                        for i in range(phone):
                            start_time += phones[i]['duration']
                        time.append(start_time * 1000)
                        end_time = start_time
                        for j in range(phone, phone + 3):
                            end_time += phones[j]['duration']
                        time.append(end_time * 1000)
                        times.append(time)
    return times

def get_word_times(chosen_word, json_file):
    times = []
    for word in json_file['words']:
        if 'phones' in word:
            if word['word'] == chosen_word:
                print("yay")
                time = []
                time.append(word['start'] * 1000)
                time.append(word['end'] * 1000)
                times.append(time)
    return times

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
                if isVowel(curr_phone[0]):
                    time = []
                    time.append(curr_phone)
                    time.append(start_time * 1000)
                    start_time += phone['duration']
                    time.append(start_time * 1000)
                    times.append(time)
                else:
                    start_time += phone['duration']
    return times




######################################################################################################################################





def main():
    triphones = {}
    alignments = []
    times = []
    words = {}

    firstLine = 0

    with open('sample_files.tsv', 'r') as samples:
        rd = csv.reader(samples, delimiter="\t")
        for sample in rd:
            if firstLine > 0:
                audio_file = sample[1]
                accent = sample[7]
                audio_file = audio_file.replace(".mp3", "").strip()
                with open("transcript.txt", 'w') as temp:
                    temp.write(sample[2])
                temp.close()
                text_file = "transcript.txt"
                # open audio files
                #audio_file = "common_voice_en_20241862"
                print('aligning', "data/"+audio_file)
                json_data = send_request("data/"+audio_file, text_file)
                #json_data = json.load(json_data)

                #json_data = json.loads(json_data)
                temp = []
                temp.append(audio_file)
                temp.append(json_data)
                temp.append(accent)
                alignments.append(temp)
            firstLine += 1

    for alignment in alignments:

        #new_times = get_word_times("and", alignment[1])
        new_times = get_vowel_times(alignment[1])

        print(new_times)



        if new_times:
            count = 0
            for time in new_times:
                #print(time[0], time[1])
                #print("data/"+alignment[0])
                test = trim_audio("data/"+alignment[0], time[1], time[2], time[0], alignment[2], count)
                count += 1

    # trim audio
    #start = 6970.0
    #end = 7239.999999999999

    #test = trim_audio(audio_file, start, end)

if __name__ == '__main__':
    main()
