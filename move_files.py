import shutil
import os
import csv

source = "/home/chai/data/MozillaCommonVoice/clips/"
dest = "/home/chai/data/MozillaCommonVoice/sample_500/"

firstLine = 0

accent = 'african'
num_per_accent = 0

with open('samples_500.csv', 'w', newline = '') as chosen:
    write_samp = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    with open('Clustering_train_1000each.csv', 'r') as samples:
        rd = csv.reader(samples, delimiter=",")
        for sample in rd:
            if firstLine > 0:
                if accent == sample[7]:
                    if num_per_accent <= 500:
                        num_per_accent += 1
                        audio_file = sample[1]
                        write_samp.writerow(sample)
                        shutil.copy(source+audio_file, dest)
                    else:
                        continue
                else:
                    print(accent, sample[7])
                    print(num_per_accent)
                    accent = sample[7]
                    num_per_accent = 1
                    audio_file = sample[1]
                    write_samp.writerow(sample)
                    shutil.copy(source+audio_file, dest)
            firstLine += 1
