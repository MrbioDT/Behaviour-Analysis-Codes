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
from bouts import *
from dt_tools_function_vol_1 import readallfiles,readcsv_outputdict,string2number_list,mouth_movement_value, rename_csv



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

    ### DT'S DATA
    ### Part1- READ SHV TAIL FITTING ###
    input_folder = 'C:\DT files\Julie Semmelhack Lab\Code\Behavioral Analysis\Tail Movement Comparison\Head-fixed strike'
    filenames = os.listdir(input_folder)
    shvs = [filename for filename in filenames if os.path.splitext(filename)[1] == '.shv']
    csvs = [filename for filename in filenames if os.path.splitext(filename)[1] == '.csv']

    strike_bout = []

    count = 0
    for shv in shvs:
        t = shelve.open(input_folder+'\\'+shv)

        print '*************************************'
        print shv
        print csvs[count]
        print '++++++++++++++++++++++++++++++++++++++++++++++++++++++'

        for key in t.keys():
            t = t[key].tailfit #(x,y), fitting tail point, frame

            print shv, ' fitting tail points are ', len(t[0])

            angles = tail2angles(t)
            boutedges, var = extractbouts(angles)  # tag

            csv_file_dic = readcsv_outputdict(input_folder+'\\'+csvs[count])  # put the csv into a dictionary
            count += 1
            final_strike = csv_file_dic['final_striking']

            for frame in strike_frames:
                for bout in boutedges:
                    if bout[0] <= frame <= bout[1]:
                        strike_bout.append(t[bout[0]:bout[1]])
                        boutedges.remove(bout)
                        break

    tailfreq_mean = []; tailamplitude_mean = []; tailamplitude_max = []; boutduration = []; tailasymmetry = []; tailvigour = []

    for bout in strike_bout:

        nFrames = len(bout)
        boutangle = tail2angles(bout, direction='down')  # extract the tailfits of the bout frames
        velocity = np.diff(boutangle)
        peak = peakdetector.peakdetold(boutangle, 3)  ### parameters!!!

        Fs = 1 / float(300)  ### parameters!!! 500 for duncan, 300 for dt
        p = 0;
        n = 0
        for angle in boutangle:
            if angle >= 0:
                p += 1
            else:
                n += 1

        if abs(max(boutangle))<= abs(min(boutangle)):
            tailamplitude_max.append(abs(min(boutangle)))
        else:
            tailamplitude_max.append(abs(max(boutangle)))

        tailamplitude_mean.append(sum(boutangle) / float(len(boutangle)))
        tailfreq_mean.append((len(peak[0]) + len(peak[1])) / float((2 * Fs * nFrames)))
        boutduration.append(float((Fs * nFrames)))
        tailasymmetry.append(p / float(n + p))  ### Question. maybe want to refine this?

        time = 120
        vigour = 0
        for i in range(int(time / (1000 / 300))):
            try:
                vigour = vigour + abs(velocity[i]) * 2 ###this is the problem!!!
            except:
                print i, len(velocity)
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
    data = pd.DataFrame(dict(tailfreq_mean=tailfreq_mean, tailamplitude_max=tailamplitude_max, tailamplitude_mean=tailamplitude_mean,boutduration=boutduration, tailasymmetry=tailasymmetry, tailvigour=tailvigour),
           index=range(0, len(tailfreq_mean)),columns=['tailfreq_mean', 'tailamplitude_max', 'tailamplitude_mean', 'boutduration', 'tailasymmetry','tailvigour'])
    csv_name = 'head-fixed_strike.csv'
    output_path = os.path.join('results\\' + csv_name)
    data.to_csv(output_path)

