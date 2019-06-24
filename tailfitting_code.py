# Modified by DT on 2019 June 24th
# most updated version of tailfitting code with following function
# 1. click the first_point close to the swim bladder
# 2. batch processing, can choose to display the tailfitting or not
# 3. scaling, change the image of video size in case the video are too large
# 4. save the parameters into csv
# 5. regulate how tight the fitting of tail tips should be: directly change the parameter 'tailedges_thresh' in tailfit function
# this would be the most concise version of tailfitting

import pandas as pd
import os
from tailfit9 import *

if __name__ == "__main__":

    ### PART-1. USER INPUT HERE ###

    ### 1-1. INPUT BASIC PARAMETERS FOR PLOT ###
    #folder = 'F:\Hard-Disk DT-1 backup 20190101\DT-data 20190101 backup\\2018\strike_data single para\\frontal strike_binocular'  #this should be the folder where you put all the videos for analysis # folder = pickdir() # alternative way to do
    folder = 'F:\Hard-Disk DT-1 backup 20190101\DT-data 20190101 backup\\2018\May\May 28_low density\\20180528_1st\\videos'
    folder = 'F:\Hard-Disk DT-1 backup 20190101\DT-data 20190101 backup\\2018\May\May 28_low density\\20180528_2nd\\videos\strike'
    folder = 'F:\Hard-Disk DT-1 backup 20190101\DT-data 20190101 backup\\2018\May\May 9\\20180509_3rd_1st recording\\videos\strike candidates'
    folder = 'F:\Hard-Disk DT-1 backup 20190101\DT-data 20190101 backup\\2018\May\May 16_low density\\5th_fish_2nd_recording\\videos\strike_candidate\good fitting'
    folder = 'F:\Hard-Disk DT-1 backup 20190101\DT-data 20190101 backup\\2018\June\June 11_low density\\20180611_t1\\videos\strike\single para'

    output_folder = 'F:\Analysis\\20190620 tailfitting'
    tail_firstpoint = None
    tail_startpoint = None
    scale = 0.75 # scaling for tail-fitting

    ### 1-2. INPUT THRESH PARAMETERS FOR ANALYSIS ###
    # READ ALL THE AVIS FILES WITHIN THAT FOLDER
    filenames = os.listdir(folder)
    avis = [filename for filename in filenames if os.path.splitext(filename)[1] == '.avi']

    ### PART-2. SET THRESHOLD, PLOT DATA AND SAVE ###
    ### ANALYSIS STARTS HERE (LOOP THROUGH EACH AVI FILE IN SELECTED FOLDER) ###
    for avi in avis:
        print '******************************************************************************************************************'
        print 'current processing is: ', avi  # tell the user which avi is processing

        ### 2-4. SETTING TAIL STARTING POINT, SAVE TO SHV ###
        display = True
        displayonlyfirst = True

        'TAIL FITTTING'
        video_path = str(folder + '\\' + avi)
        if str(type(tail_startpoint)) == "<type 'NoneType'>":
            # you can either set the startpoint or process the same batch of videos with the startpoint setted in the first videos
            tail_firstpoint, tail_startpoint, tailedges_thresh = tailfit_batch([video_path], display, displayonlyfirst,shelve_path=output_folder + '\\' + avi + '_tail.shv',
                                                                                   reuse_startpoint=True, scale=scale)
        else:
            display = False
            displayonlyfirst = False
            tail_firstpoint, tail_startpoint, tailedges_thresh = tailfit_batch([video_path], display, displayonlyfirst, shelve_path=output_folder + '\\' + avi + '_tail.shv',
                                                                                   reuse_startpoint=True, tail_startpoint=tail_startpoint, tail_firstpoint = tail_firstpoint, scale=scale)


    ### SAVE THE PARAMETERS ###

    df = pd.DataFrame({'scale':[scale],'firstpoint':[tail_firstpoint],'startpoint':[tail_startpoint],'tailedges_thresh':[tailedges_thresh]})
    # tailedges specifies how tight the tailfitting is
    df.to_csv(output_folder + '\\parameters.csv')
