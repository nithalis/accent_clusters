# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 16:04:14 2020

@author: SAAKSHI
"""

from pydub import AudioSegment
import json
import numpy as np
import python_speech_features
import pydub
import matplotlib.pyplot as plt
from pydub import AudioSegment
import IPython
import scipy
from python_speech_features import logfbank
from python_speech_features import mfcc
import scipy.cluster.hierarchy as sch
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.cluster import AgglomerativeClustering
import pydub
from scipy.spatial.distance import pdist, euclidean
from fastdtw import fastdtw
#from dtaidistance import dtw
import os
import math
from collections import Counter

# choose the label and phone

label_choice = input("Choose Label: accent (a) | phone (p) | recording (r): ")
phone_choice = input("Select phone: all (a) | distinguished (d) | [type phone]: ")

all = True
phone_list = []
# deciding the phone list
if phone_choice != "a":
    all = False
    if phone_choice == 'd':
        phone_list = ['ow', 'ih', 'er', 'aa']
    else:
        phone_list = [phone_choice]



# setting the folder

all_mfccs = []
accents={'african':[],'canada':[],'england':[],'indian':[],'ireland':[],'malaysia':[],'scotland':[]}

labels = []
path = r'C:\Users\Sharaf DG\Desktop\try'
  
# Get the list of all files and directories 
# in current working directory 
dir_list = os.listdir(path)
cnt = 0
for audio_name in os.listdir(r'C:\Users\Sharaf DG\Desktop\try'):
    if ".DS_Store" in audio_name:
        continue
    if not all:
        if audio_name[:2] in phone_list:
            
            # audio to mfccs
            #audio = os.path.join("monophones", audio_name)
            audio = 'C:\\Users\Sharaf DG\Desktop\\try' + "\\" + audio_name
            #print(audio)
            segment = AudioSegment.from_file(audio)
            samples = segment.get_array_of_samples()
            fbank_feat = mfcc(np.array(samples))
            m, n = fbank_feat.shape
            fbank_feat = fbank_feat.reshape(1, m*n)
            all_mfccs.append(fbank_feat)

            name_split = audio_name.split("_")
            # extract label
            if label_choice == 'a':
                label = name_split[2]
                labels.append(label)

            elif label_choice == 'p':
                label = name_split[0] + "_" + name_split[1]
                acc_name = name_split[2]
                accents[acc_name].append(cnt)
                labels.append(label)

            else:
                label = ""
                for word in name_split[4:8]:
                    label += word
                labels.append(label)


    else:

        # audio to mfccs
        audio = 'C:\\Users\Sharaf DG\Desktop\\try' + "\\" + audio_name
        # print(audio)
        segment = AudioSegment.from_file(audio)
        samples = segment.get_array_of_samples()
        fbank_feat = mfcc(np.array(samples))
        m, n = fbank_feat.shape
        fbank_feat = fbank_feat.reshape(1, m*n)
        all_mfccs.append(fbank_feat)

        name_split = audio_name.split("_")
        # extract label
        if label_choice == 'a':
            label = name_split[2]
            labels.append(label)

        elif label_choice == 'p':
            label = name_split[0] + "_" + name_split[1]
            acc_name = name_split[2]
            accents[acc_name].append(cnt)
            labels.append(label)

        else:
            label = ""
            for word in name_split[4:8]:
                label += word
            labels.append(label)


    cnt+=1


m = ([len(accents[i]) for i in accents])
m = np.min(m)
new_list=[]
for i in accents:
    s = accents[i]
    s = s[:m]
    accents[i] = s
    new_list = new_list + s
    
new=[]
# similarity metric to compare all recordings to each other
for i in range(len(all_mfccs)):
    if i in new_list:
        new.append(all_mfccs)
all_mfccs = new
all_mfccs = np.asarray(all_mfccs)
x = len(all_mfccs)
similarity = np.zeros((x,x))

for i in range(x):
    m1 = all_mfccs[i]
    for j in range(x):
        m2 = all_mfccs[j]
        similarity[i,j],_ = fastdtw(m1.T,m2.T, dist=euclidean)
ds=similarity


#ds = dtw.distance_matrix_fast(all_mfccs)

print(ds)
print()
ds[ds == math.inf] = 0
ds_T = ds.T
ds = ds+ds_T

#max = np.amax(ds)

#ds[ds == -1] = max + 5


# dendrogram to cluster
linked = linkage(ds, 'ward')

sch.dendrogram(linked, labels=labels)
plt.gcf()
plt.savefig("dendrogram_"+str(phone_choice)+"_sample.png")


# now actually choosing the cluster
num_clusters = input("How many clusters? ")

clustering = AgglomerativeClustering(n_clusters = int(num_clusters)).fit(ds)
print(clustering.labels_)
print()
assigned_clusters = np.array(clustering.labels_)

print(Counter(labels))

# for each cluster
for cluster in range(int(num_clusters)):
    plt.figure()
    within = np.where(assigned_clusters == cluster)[0]
    cluster_dict = {}

    for index in within:
        if labels[index] in cluster_dict:
            cluster_dict[labels[index]] += 1
        else:
            cluster_dict[labels[index]] = 1


    vals = list(cluster_dict.values())
    keys = list(cluster_dict.keys())

    max = np.argmax(vals)
    print(vals)
    print(max)
    print(keys[max])

    exp = np.zeros(len(vals))
    exp[max] = 0.1

    # now create a chart
    plt.pie(vals, explode = exp, autopct='%1.0f%%', labels=keys, shadow=True, startangle=90)

    plt.gcf()
    plt.savefig("cluster_" + str(cluster) + ".png")


print("All done!")