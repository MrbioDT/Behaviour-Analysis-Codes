# Note. Modulize the code, make it easy to read
# This version is particularly for Duncan's data...

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import shelve
import os
from framemetrics import *
import peakdetector

def animate_normalizedshv(tailfit, key):

    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=12, metadata=dict(artist='Me'), bitrate=1800)
    # fps, Framerate for movie...
    # Q. if this fps will affect the display speed?
    # Note. actually, we are not very strict about playing speed...

    fig = plt.figure(figsize=(5, 6.5))
    frame_list = []
    # for i in range(0, 200):
    #     frame_list.append(i + 1000)
    ani = matplotlib.animation.FuncAnimation(fig, normalizedshv, frames=len(tailfit), interval=80, repeat=False, fargs=tailfit)
    ani.save(key + '_fps12.mp4', writer=writer)
    #plt.show()
    return 0

def normalizedshv(i,*tailfit):
    plt.clf()
    x=[]
    y=[]
    for item in tailfit[i]:
        # plt.title('tailfit plotting', fontsize=20)
        # plt.plot(item[1], item[0], 'ro')
        x.append(item[0])
        y.append(-item[1])
    plt.xlim(-0.5, 0.5)
    plt.ylim(-1.2, 0.1)
    plt.plot(x, y, color='black', marker='o', linestyle='solid', linewidth=3, markersize=2)
    #plt.show()
    #plt.clf()
    return 0

if __name__ == "__main__":

    ###INPUT THE TAIL BOUTS IN BIG LIST###

    # ### DT'S DATA
    # ### Part1- READ SHV TAIL FITTING ###
    # input_folder = 'C:\DT files\Julie Semmelhack Lab\Code\Behavioral Analysis\Animated Tail Movement\dt_shv'
    # filenames = os.listdir(input_folder)
    # shvs = [filename for filename in filenames if os.path.splitext(filename)[1] == '.shv']
    # for shv in shvs:
    #     t = shelve.open(input_folder+'\\'+shv)
    #     for key in t.keys():
    #         t = t[key].tailfit
    #         t = np.array(t)
    #         print t.shape

    bout_type = 'spontaneous'
    bout_type = 'prey_capture'
    bout_type = 'sstrike'
    bout_type = 'attack'

    tail_points = np.load('C:\DT files\Julie Semmelhack Lab\Code\Behavioral Analysis\Tail Movement Comparison\Duncan_data\\'+ bout_type + '_points.npy')  # file containing tail points for each bout
    indexer = np.load('C:\DT files\Julie Semmelhack Lab\Code\Behavioral Analysis\Tail Movement Comparison\Duncan_data\\'+ bout_type + '_indexer.npy')  # file containing indices of the first and last frames for each bout

    tailfreq_mean = []; tailamplitude_mean = []; tailamplitude_max = []; boutduration = []; tailasymmetry = []; tailvigour = [];

    # parameters calculation!
    for i, j in zip(indexer, indexer[1:]):
        ps = tail_points[i:j]

        nFrames = len(ps)
        boutangle = tail2angles(ps,direction = 'left')  # extract the tailfits of the bout frames
        velocity = np.diff(boutangle)
        peak = peakdetector.peakdetold(boutangle, 4) ### parameters!!!

        Fs = 1 / float(500)  ### parameters!!! 500 for duncan, 300 for dt
        p = 0; n = 0
        for angle in boutangle:
            if angle >= 0:
                p += 1
            else:
                n += 1

        if abs(max(boutangle))<= abs(min(boutangle)):
            tailamplitude_max.append(abs(min(boutangle)))
        else:
            tailamplitude_max.append(abs(max(boutangle)))
        tailamplitude_mean.append(sum(boutangle)/float(len(boutangle)))
        tailfreq_mean.append((len(peak[0])+len(peak[1])) / float((2*Fs * nFrames)))
        boutduration.append(float((Fs * nFrames)))
        tailasymmetry.append(p/float(n+p))  ### Question. maybe want to refine this?

        time = 120
        vigour = 0
        for i in range(int(time/(1000/500))):
            try:
                vigour = vigour + abs(velocity[i])*2
            except:
                print i,len(velocity)
                break

        tailvigour.append(vigour)

        # # plot and validation session
        # plt.plot(boutangle)
        # for p in peak[1]:
        #     plt.plot(p[0],p[1],'ro')
        # for p in peak[0]:
        #     plt.plot(p[0],p[1],'ro')
        # plt.show()
        # plt.plot(velocity)
        # plt.show()

    ### TAKE THE BIG LIST AND CALCULATE THE PARAMETERS OUT OF IT ###
    ### FOR EACH TAIL BOUT

    ### OUTPUT THE VALUE IN CSV
    data = pd.DataFrame(dict(tailfreq_mean=tailfreq_mean, tailamplitude_max=tailamplitude_max, tailamplitude_mean = tailamplitude_mean,boutduration=boutduration,tailasymmetry=tailasymmetry,tailvigour=tailvigour),
                        index=range(0, len(tailfreq_mean)),columns=['tailfreq_mean','tailamplitude_max','tailamplitude_mean','boutduration','tailasymmetry','tailvigour'])
    csv_name = bout_type + '.csv'
    output_path = os.path.join('results\\'+csv_name)
    data.to_csv(output_path)


