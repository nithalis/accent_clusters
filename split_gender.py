import csv
import os
import shutil

females = []
males = []
source = os.path.join(os.getcwd(), "cut_audio/")
dest_f = os.path.join(os.getcwd(), "females/")
dest_m = os.path.join(os.getcwd(), "males/")
count = 0

firstLine = 0
with open('samples_500.csv', 'r') as sample:
    rd = csv.reader(sample, delimiter=",")
    for sample in rd:
        if firstLine > 0:
            audio_file = sample[1]
            gender = sample[6]
            print(gender)
            audio_file = audio_file.replace(".mp3", "").strip()
            if gender == "female":
                #print(gender)
                females.append(audio_file)
            elif gender == "male":
                #print(gender)
                males.append(audio_file)
        firstLine += 1

#print(firstLine)
all_audio = os.listdir(source)
new_count = 0

#print(males)

for audio in all_audio:
    if ".DS_Store" in audio:
        continue
    name_split = audio.split("_")
    #print(name_split)
    name = name_split[0] + "_" + name_split[1] + "_" + name_split[2] + "_" + name_split[3] + "_"
    words = name_split[4:8]
    label = words[0]
    for word in words[1:4]:
        label += "_" + word


    word_name = label.replace(".wav", "").strip()

    whole = name + label
    if word_name in females:
        shutil.copy(source+whole, dest_f)
    elif word_name in males:
        shutil.copy(source+whole, dest_m)

#print(count, new_count)
