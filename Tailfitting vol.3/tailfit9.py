'''Running enviornment: python 2.7, opencv 2.4.9'''

__version__ = '0.9.3'

import matplotlib.pyplot as plt
import copy
import cv2
import time
import numpy as np
import pylab, os
import pdb
import shelve
import sys
from PIL import Image
import scipy.ndimage
import scipy.stats
import hashlib
from tailfitresult import *
import numpy as np
from inspect import getmembers, isclass, isfunction, getmoduleinfo, getmodule
import sys
from scipy import fft
import matplotlib.pyplot as plt

def normalizetailfit(tailfit):
    """Takes in a tailfit, and returns a normalized version which is goes from 0 to 1 normalized to taillength averaged over the first few frames"""
    # Note. Just remind you what tailfit is:
    # NOTE. CONFIRMED. fitted_tail is the final result of the whole program.
    # NOTE. CONFIRMED. it is a list, storing arrays with the total number of total frame analyzed/read
    # NOTE. CONFIRMED. each correspond to one frame, storing x number of points (x=tail_lengh/count)
    # NOTE. CONFIRMED. points is the fitted result_point(mid point of tail edge), it is the coordinate in each frame
    # NOTE. CONFIRMED. count would be the final number of total circles.

    tail_length = (tailfit[0][-1,:]-tailfit[0][0,:]).max()   #tag
    # Question. difficult why calculate tail_length in such way?

    return [(frame-frame[0,:]).astype(float)/float(tail_length) for frame in tailfit]
    # Question. why normal this way?
    # Question. whether this return could normalize to 0 to 1? doubt it.
    # ndarray.astype(dtype, order='K', casting='unsafe', subok=True, copy=True).  Copy of the array, cast to a specified type.

def hashfile(afile, hasher, blocksize=65536):
    # shahash = hashfile(open(videopath, 'rb'), hashlib.sha256())
    buf = afile.read(blocksize)
    # Question. in which library is read defined?
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.digest()

def normalizetailfit(tailfit):
    """Takes in a tailfit, and returns a normalized version which is goes from 0 to 1 normalized to taillength averaged over the first few frames
    """
    tail_length = (tailfit[0][-1,:]-tailfit[0][0,:]).max()
    return [(frame-frame[0,:]).astype(float)/tail_length for frame in tailfit]
    #could angular adjust, and maybe take average of some non-moving frames

def sliding_average(somelist, window_size = 10):
    somelistpadded = np.lib.pad(somelist,(window_size/2,window_size/2),'edge')
    return np.convolve(somelistpadded, np.ones(int(window_size))/float(window_size),mode='valid')

def sliding_gauss(somelist, window_size = 10,sigma=3):
    somelistpadded = np.lib.pad(somelist,(window_size/2,window_size/2),'edge')
    normpdf = scipy.stats.norm.pdf(range(-int(window_size/2),int(window_size/2)),0,sigma)
    return np.convolve(somelistpadded,  normpdf/np.sum(normpdf),mode='valid')[:len(somelist)]

def handleclick(event,x,y,flags,param):
    if event==cv2.cv.CV_EVENT_LBUTTONDOWN:
        param[0]=x
        param[1]=y


def tail_func2(x, mu, sigma, scale, offset):
    # Question. what does this function means...
    # A. seems to be a Gaussian?
    return scale * np.exp(-(x-mu)**4/(2.0*sigma**2))**.2 + offset #

##################################################################
def zeroone(thing):
    return (thing-thing.min())/(np.percentile(thing,99)-thing.min())
def scalesize(frame, multiple):
    return cv2.resize(frame,(frame.shape[0]*multiple,frame.shape[1]*multiple))
#######

def tailfit(filename,display=None,start_point=None, direction='down', output_jpegs = False, plotlengths = False, tail_startpoint = None, tail_firstpoint = None, scale = 0.5):
    # avi, 1st time:   fittedtail,startpoint,  direction, FPS, numframes  = tailfit(videopath,(first or not displayonlyfirst) and display ,startpoints)
    # fittedtail,startpoint,  direction, FPS, numframes  = tailfit(videopath,(first or not displayonlyfirst) and display ,startpoints[i])
    '''
    Takes an avi filepath, fits the tail of the fish
    Display sets if the fit is shown as it is processed (slower)
    Start point is where fitting begins, if None the user is queried
    Direction is which direction the fit happens
    '''

    '''1ST PART. INITIATE THE PARAMETERS AND READ THE FRAME'''
    directions={"up":[0,-1],"down":[0,1],"left":[-1,0],"right":[1,0]}
    fitted_tail=[]
    cap = cv2.VideoCapture(filename)
    if not cap.isOpened():
        print "Error with video or path!"
        raise Exception('Issues opening video file!')

    frame=cap.read()[1]
    frame = cv2.resize(frame, (0,0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)  #[ADJUST] resize-tag #resize the frame!
    # Question. abt the grammar? why not start from [0]
    # Answer. cv2.VideoCapture.read([image]) returns tuple (retval, image), so frame only takes the returned image
    cv2.destroyAllWindows()

    max_points = 200   # mostly in case it somehow gets stuck in a loop, and to preallocate the result array
    frame_fit=np.zeros((max_points,2))  # frame_fit is a 2d array, tuple inside the np.zeros() defines the shape of frame
    first_frame=True  # first_frame just told the program if it is processing the first frame
    widths, convolveresults = [],[]
    test,slices = [], []


    '''2ND PART. ANALYSIS FRAME ONE BY ONE'''
    while type(frame) != type(None):
    # LOOP NO.1 while is the biggest loop, it continutes until analysis of the 1st frame.
    # Question. how to break this loop?
    # Answer. At the end, when next read of frame returns None

        if display:   # display in main-function is boolean
            frame_display=frame.copy()
        if direction:
            guess_vector = np.array(directions[direction]) # guess_vector represent which direction the fit happens
        else:
            raise Exception('Need to define a direction!') #could ask here

        '''2-1. IF FIRST FRAME'''
        '''This 2-1. session is only implemented one time during the 1st frame'''
        if first_frame:
        # Note, first_frame=True, this is defined outside the while loops

            #TODO try to ID the head?
            #predict tail pos, and dir?
            #then query user for ok
            #detect things aligned the same as before, by looking for big shifts between first frames of video?

            '''2-1.0 SET THE FIRST-POINT''' #tag #add this one more click to get the point close to swim bladder
            if str(type(tail_firstpoint)) != "<type 'NoneType'>":
                current = tail_firstpoint
                first_point = tail_firstpoint
            else:
                handlec = handleclick # use this function: def handleclick1(event,x,y,flags,param):
                cv2.namedWindow('first_point')
                cv2.imshow("first_point", frame)
                cv2.moveWindow('first_point', 0, 0) # would be nice to raise window, since it doesn't always spawn top
                cv2.waitKey(10)
                f_point = np.array([-1, -1])
                cv2.setMouseCallback("first_point", handlec, f_point) # cv2.setMouseCallback(windowName, onMouse[, param])
                print "Click on the first_point of the fish's tail"
                cv2.waitKey(10)  # Question. difference between 0 and 10?    #tag
                while (f_point == np.array([-1, -1])).all():  # Question. this all() is strange ... Answer. point is a list/array
                    cv2.waitKey(10)
                current = f_point
                first_point = current
                print 'first point is ', first_point
                # the start_point is set here.... it seems to be correlated to threshold as well?
                cv2.destroyWindow('first_point')

            '''2-1.1 SET THE STARTPOINT'''
            #SET THE STARTPOINT. if we don't have a start point, query user for one
            if type(start_point)==type(np.array([])) or type(start_point) is list:
                f_current = np.array(start_point)
                point = f_current
            elif str(type(tail_startpoint)) != "<type 'NoneType'>":
                start_point = tail_startpoint
                point = start_point
                f_current = start_point
            else:
                handlec=handleclick # use this function: def handleclick(event,x,y,flags,param):
                cv2.namedWindow('first')
                cv2.imshow("first",frame)
                cv2.moveWindow('first',0,0)
                #would be nice to raise window, since it doesn't always spawn top

                cv2.waitKey(10)
                point = np.array([-1,-1])
                cv2.setMouseCallback("first",handlec,point)  # cv2.setMouseCallback(windowName, onMouse[, param])
                print "Click on start of the fish's tail"
                cv2.waitKey(10)  # Question. difference between 0 and 10?    #tag
                while (point == np.array([-1,-1])).all(): # Question. this all() is strange ... Answer. point is a list/array
                    cv2.waitKey(10)
                f_current = point
                start_point = f_current
                print 'start point is ', start_point
                # the start_point is set here.... it seems to be correlated to threshold as well?
                cv2.destroyWindow('first')
                # TODO Simplify the code, too redunctant

            # NOTE. CONFIRMED. current can be accessed outside the if & else

            '''2-1.2 ILLUMINATION ANALYSIS FOR BG & FISH'''
            # BUILD THE HISTOGRAM, frame is np.ndarray, 2D-gray scale, 3D-RGB
            if frame.ndim == 2:
                hist = np.histogram(frame[:,:],10,(0,255))
                # Question. 255 can't be divided by 10?   A. 10 means the number of bars, not the interval
                # hist/returned value of np.histogram is a tuple, the first item is occurrence in each bin, the second item is bin
                # numpy.histogram(a, bins=10, range=None, normed=False, weights=None, density=None)
                # If bins is an int, it defines the number of equal-width bins in the given range (10, by default). If bins is a sequence, it defines the bin edges, including the rightmost edge, allowing for non-uniform bin widths.
            elif frame.ndim == 3:
                # Task. maybe this loop for RGB vedios, try this later
                hist = np.histogram(frame[:,:,0],10,(0,255))
                # Question. the meaning of this sentence?
                # Question. if frame is 3D then it should be converted into gray scale??? Can't just take R to construct histogram
            else:
                raise Exception('Unknown video format!')

            # find background - 10 bin hist of frame, use most common as background
            background = hist[1][hist[0].argmax()]/2+hist[1][min(hist[0].argmax()+1,len(hist[0]))]/2
            if frame.ndim == 2:
                fish = frame[point[1]-2:point[1]+2,point[0]-2:point[0]+2].mean()
            elif frame.ndim == 3:
                fish = frame[point[1]-2:point[1]+2,point[0]-2:point[0]+2,0].mean()

            '''2-1.3 BUILD THE GAUSSIAN KERNEL & SET DISPLAY '''
            print "Starting tailfit on:  ", filename
            FPS = cap.get(cv2.cv.CV_CAP_PROP_FPS)  # CV_CAP_PROP_FPS represent Frame rate
            numframes = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)) # total frame number
            guess_line_width = 51
            normpdf = pylab.normpdf(np.arange((-guess_line_width+1)/4+1,(guess_line_width-1)/4),0,8)

            if display:
                cv2.namedWindow("frame_display")
                cv2.moveWindow("frame_display",0,0)
            starttime = time.time()
            # Return the current time in seconds since the Epoch.
        else:
            current= fitted_tail[-1][0,:]

        '''2-2. SET SPACING'''
        tailpoint_spacing = 5

        '''2-3.FIT THE TAIL WITH CIRCILES IN THIS FRAME(BIG FOR COUNT LOOPS)'''

        for count in range(max_points):

            if current[1] <= start_point[1]:
                if count == 0:
                    newpoint = current
                    fcount = count
                else:
                    guess = current + guess_vector * tailpoint_spacing
                    newpoint = guess
            else:
                '''2-3.1 SET THE GUESS POINT/GUESS_LINE'''
                '''2-3.1.1 GUESS IS THE NEXT FITTED POINTS'''
                if count == 0:
                    guess = current  ###tag
                    # Question. what is current? A. should be the startpoint
                    # task. temp skip the following case
                elif count == 1:
                    # DT-CODE:
                    # print 'count: ', count
                    # print 'guess_vector: ', guess_vector
                    # print 'current: ', current
                    # print 'before calculation guess is: ', guess
                    guess = current + guess_vector*tailpoint_spacing #can't advance guess vector, since we didn't move from our previous point
                    # DT-CODE: print 'after calculation guess is: ', guess
                    # Question. what is the difference between guess and new_point?
                    # A. it's like guess just confirm the location of guess_slice, guess can be close to new_point, but may not be the same
                    # A. new_point is the accurate fit based on the estimation of illumination
                else:
                    guess_vector = guess_vector/(((guess_vector**2).sum())**.5) #normalize guess vector
                    # Question. what if you did not normalize it?
                    # A. you will get only two point with large interval
                    guess = current + guess_vector*tailpoint_spacing

                '''2-3.1.2 DRAW THE START AND END'''
                # TASK-DIFFICULT TO UNDERSTAND THE SEMANTIC
                # NOTE. start and end is a line vertical to the direction of tail with length of guess_line_width
                guess_line_start = guess + np.array([-guess_vector[1],guess_vector[0]])*guess_line_width/2  #####tag
                # QUESTION. DIDN'T GET IT... WHEN DID WE GET THIS?
                # directions={"up":[0,-1],"down":[0,1],"left":[-1,0],"right":[1,0]}
                # guess here for the very first time is just start point
                guess_line_end = guess + np.array([guess_vector[1],-guess_vector[0]])*guess_line_width/2
                # Question. I understand the grammar above, but not the sematic

                x_indices = np.int_(np.linspace(guess_line_start[0],guess_line_end[0],guess_line_width))
                y_indices = np.int_(np.linspace(guess_line_start[1],guess_line_end[1],guess_line_width))
                # default interval for np.linspace should be 1
                # 51 = guess_line_width items in x_indices
                # returned x_indices & y_indices are type 'numpy.ndarray'
                # numpy.linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=None)
                # np.linspace, Return evenly spaced numbers over a specified interval.
                # num, Number of samples to generate. Default is 50. Must be non-negative.
                # NumPy knows that int refers to np.int_

                '''2-3.1.3 JUDGE IF THE CLIP IS PROPER'''
                # TASK. I am not sure how useful this session would be. wait and see
                if max(y_indices) >= frame.shape[0] or min(y_indices) < 0 or max(x_indices) >= frame.shape[1] or min(x_indices) < 0:
                # Question. I don't understand why is the x and y reversed? x should correspond to frame[0]
                # Answer. IT IS NOT REVERSED! INNER DIMENSION CORRESOPOND TO X!
                    y_indices = np.clip(y_indices,0, frame.shape[0]-1)
                    x_indices = np.clip(x_indices,0, frame.shape[1]-1)
                    print "Tail got too close to the edge of the frame, clipping search area!"
                    #TODO if too many values are clipped, break?

                '''2-3.1.4 DRAW THE GUESS_SLICE'''
                # y_indices and x_indices are np.ndarray!!!!!!
                guess_slice= frame[y_indices,x_indices]
                # guess_slice is a line that is vertical to the direction of the tail with centre as start_point with two ends as start and end
                # guess_slice is the line with each point coordinate as x & y represented by y_indices & x_indices
                # TASK DIFFICULT! the frame is transposed compared to what might be expected Question. how does this transposition work?
                # JULIE-Question. y and x always inverse?
                # Answer. IT IS NOT REVERSED! INNER DIMENSION CORRESOPOND TO X!

                # S-Question. what is the meaning of this if session?
                if guess_slice.ndim == 2:
                    guess_slice=guess_slice[:,0]
                    # Question. why only keep the first row in guess_slice
                else:
                    guess_slice=guess_slice[:]
                    # enter else for the 1st frame in avi situation

                '''2-3.2 BASELINE SUBSTRACTION'''
                if fish < background:
                    # fish is like the average grayscale/brightness of the fish image
                    guess_slice = (background-guess_slice)
                else:
                    guess_slice = (guess_slice-background)
                    # Julie-Question. why do the substraction???

                slices += [guess_slice]  ######tag
                # Question. real meaning?
                # Note. Question. difficult. they create lot of 's' to collect variables, how are they going to be used?
                hist = np.histogram(guess_slice, 10)
                guess_slice = guess_slice - guess_slice[((hist[1][hist[0].argmax()] <= guess_slice)&(guess_slice<hist[1][hist[0].argmax()+1]))].mean()  #tag
                # QUESTION. WHAT IS THE MEANING OF THIS PROCESSING?
                # Note. CONFIRMED. Baseline substraction, build a histogram and substract the the mean value of smallest bin
                # Question. principles underlying this ?
                # A. baseline substraction. draw a histogram based on guess_slice and choose the interval with most items and get the mean of these items and substracted it
                # & means only keep the items that is both true in either formula
                # only the item corresponds to true could be selected out to remain
                # Question. <=, hist[1][index] is integer, can't be comparied with guess_slice, a  right????
                # A. return value is going to be a matrix containing boolean, same shape of guess_slice

                '''2-3.3 FILTER! SMOOTH THE GUESS_SLICE '''
                # Note. this seems to do a nice job of smoothing out while not moving edges too much
                sguess = scipy.ndimage.filters.percentile_filter(guess_slice,50,5)
                #QUESTION. does this has to be length of 51??1

                # WHAT DOES THIS sguess actually do?
                # QUESTION. WILL THIS NUMBER 50 OR 5 EFFECTS THE FITTING?
                # Task. DIFFICULT! JULIE-Question. I want to know the principle of this filter and exactly how this sguess is calculated. why you choose this one
                # Note. CONFIRMED. type of sguess is <type 'numpy.ndarray'>, with 51 items, this 'filter' is not constant, change every frame?
                # scipy.ndimage.filters.percentile_filter(input, percentile, size=None, footprint=None, output=None, mode='reflect', cval=0.0, origin=0)

                '''2-3.4, 1ST FRAME-1, DELINEATE ALL THE NEWPOINT'''
                if first_frame:
                    # first time through, profile the tail
                    '''2-3.4.1 DEFINE THE EDGE OF TAIL AND FIND THE MID-POINT'''  ###tag-question... not very clear...
                    tailedges_threshold = 0.25
                    # the smaller the value, the tighter the tailfitting would be, less dots
                    tailedges = np.where(np.diff(sguess>(sguess.max()*tailedges_threshold)))[0]  #############tag... don't understand....
                    # Note. tailedges delineate the "horizontal" edge of fitting, how "wide" the tail looks like
                    # [ADJUSTMENT] The original value is .25 ....
                    # QUESTION. WHY SOMETIMES TAILEDGES COULD HAVE MULTIPLE COMPONENTS?
                    # Note. Use 1/4 of max to define the edge of tail!
                    # Note. returned tailedges is (array([17, 32])) for one frame, item correspond to the index in list
                    # numpy.where(condition[, x, y]), Return elements, either from x or y, depending on condition.
                    # numpy.diff(a, n=1, axis=-1), Calculate the n-th order discrete difference along given axis.
                    # numpy.diff would return the value correspond to True, if the two items are Boolean and different

                    if len(tailedges)>=2:
                        tailedges = tailedges-len(sguess)/2.0
                        tailindexes = tailedges[np.argsort(np.abs(tailedges))[0:2]]
                        # so this operation just sorted the tailedges, and only keep the biggest two items
                        # Question. why only keep the biggest two items???
                        # np.argsort, Returns the indices that would sort an array.
                        # DT-CODE: print '(tailindexes).mean()+len(sguess)/2.0: ', (tailindexes).mean()+len(sguess)/2.0

                        result_index_new = (tailindexes).mean()+len(sguess)/2.0
                        # QUESTION. WHY ADD len(sguess)?
                        # Note. result_index_new is the mid point of tailedges
                        # Note. this complex calculation can be replaced with: result_index_new = tailedges.mean()

                        widths +=[abs(tailindexes[0]-tailindexes[1])]
                        # Note. widths of the tail
                    else:
                        result_index_new = None
                        tail_length = count
                        # Note. means the stop of guessing!
                        break

                    '''2-3.4.2 CONVOLUTION & NEWPOINT'''
                    results = np.convolve(normpdf, guess_slice, "valid")
                    convolveresults+=[results]
                    result_index = results.argmax() - results.size/2+guess_slice.size/2
                    newpoint = np.array([x_indices[int(result_index_new)],y_indices[int(result_index_new)]])  #DT-modification: add int() here

                else:
                    #results= np.convolve(tailfuncs[count],guess_slice,"valid")
                    # Q. why perform convolution here?

                    results = np.convolve(normpdf, guess_slice, "valid")  #key modification
                    result_index = results.argmax() - results.size/2+guess_slice.size/2
                    newpoint = np.array([x_indices[result_index], y_indices[result_index]])
                    # x_indices and y_indices are things in guess_slices


            '''2-3.5, 1ST FRAME-2, DEFINE THE THE TAILLENGTH IN THE FIRST FRAME!!!'''
            if first_frame:

                '''2-3.5.1 CHECK FITTING SESSION, BREAK IF NECCESSARY'''
                # task. don't really understand the principles of this session but... let it be
                if count > 10:
                    #@ SCALE FIT GOODNESS WITH CONTRAST
                    trapz = [pylab.trapz(result-result.mean()) for result in convolveresults]   #tag
                    # Integrate along the given axis using the composite trapezoidal rule. Integrate y(x) along given axis.
                    # numpy.trapz(y, x=None, dx=1.0, axis=-1)
                    # x: array_like, optional. The sample points corresponding to the y values. If x is None, the sample points are assumed to be evenly spaced dx apart. The default is None.
                    # dx: scalar, optional. The spacing between sample points when x is None. The default is 1.
                    # Question. what is the real meaning of this...?
                    # Answer. trapz should be a list storing the 'area under curve' of convolveresults
                    # Question. why calculate sth like this?

                    slicesnp = np.vstack(slices)
                    # slices, a list storing guess_slice
                    # np.vstack, Stack arrays in sequence vertically (row wise). Just put the arrays together without changing the shape or any items.

                    if np.array(trapz[-3:]).mean() < .2:  #tag
                    # Question. what is the meaning of this array? pdb.set_trace()
                        tail_length = count  ###tag, define the length of tailin the very first frame!
                        break
                    elif slicesnp[-1,result_index-2:result_index+2].mean()<5:
                        # slicenp is a 2-d array, using -1 to access the last row, then using result_index-2:result+2 to access the corresponding part of array
                        tail_length = count
                        break
            elif count > tail_length*.8 and np.power(newpoint-current,2).sum()**.5 > tailpoint_spacing*1.5:
                break
            elif count == tail_length:
                break

            '''2-3.6 DRAW THE CIRCLES ALONG THE TAIL, UPDATE VECTORS AND THEN CURRENT'''
            if display:
                cv2.circle(frame_display,(int(newpoint[0]),int(newpoint[1])),2,(0,0,0))    #tag
                # DT CODE: print 'newpoint: ', newpoint
                # Note. CONFIRMED: circle is drawed one by one, newpoint is simple list consists of two items
                # cv2.circle(img, center, radius, color[, thickness[, lineType[, shift]]]), returns img
                # frame_display is defined by this: frame_display=frame.copy()
                # frame_display[y_indices,x_indices]=0
            frame_fit[count,:] = newpoint
            # frame_fit=np.zeros((max_points,2))
            # put the newpoint into the frame_fit array, a 2D array

            if current[1] <= start_point[1]:
                guess_vector = guess_vector
            elif current[1] <= start_point[1]+5:
                guess_vector = np.array(directions[direction])
            else:
                guess_vector = newpoint-current

            # Question. function of this if block?
            # A. guess_vector gives the direction of guess, current is old point

            current = newpoint
            # update the current with the newpoint

        '''2-4. STRANGE SWIDTHS, FINALLY! JUMP OUT OF FOR-COUNT'''
        if first_frame:
            swidths = scipy.ndimage.filters.percentile_filter(widths,50,8)  #task...temporarily just keep it
            swidths = np.lib.pad(swidths,[0,5],mode='edge')  #tag bug
            # Note. Bug. IndexError: index -1 is out of bounds for axis 0 with size 0
            # np.lib.pad, choose the last item of swidths and add
            # Question. why pads the fish?
            # numpy.pad(array, pad_width, mode, **kwargs), Pads an array

            tailfuncs = [tail_func2(np.arange((-guess_line_width+1)/4+1,(guess_line_width-1)/4),0, swidth, 1, 0) for swidth in swidths]  #tag
            # tag. Question. what's the fucking function of this one?
            # Note. guess_line_width = 51
            # Note. def tail_func2(x, mu, sigma, scale, offset)
            # Question. so swidth is going to be sigma? why is that????

        '''2-5. APPEND FITTED_TAIL'''
        fitted_tail.append(np.copy(frame_fit[:count]))

        # DT-CODE: print 'fitted_tail looks like this: ', fitted_tail
        # NOTE. CONFIRMED. fitted_tail is the final result of the whole program.
        # NOTE. CONFIRMED. it is a list, storing arrays with the total number of total frame analyzed/read
        # NOTE. CONFIRMED. each correspond to one frame, storing x number of points (x=tail_lengh/count)
        # NOTE. CONFIRMED. points is the fitted result_point(mid point of tail edge), it is the coordinate in each frame
        # NOTE. CONFIRMED. count would be the final number of total circles.

        '''2-6. DISPLAY THE FRAME!'''
        if display:
            cv2.putText(frame_display,str(count),(340,25),cv2.FONT_HERSHEY_SIMPLEX, 1.0,(225,10,20) );
            cv2.putText(frame_display,str(len(fitted_tail)-1),(15,25),cv2.FONT_HERSHEY_SIMPLEX, 1.0,(25,10,20) ); #-1 because the current frame has already been appended
            cv2.imshow("frame_display",frame_display)
            # cv2.waitKey(0)  #DT-CODE: Manual control to analyze the frame one by one
            if first_frame:
                delaytime = 1
                # Question. unit ms?
            else:
                minlen = min([fitted_tail[-2].shape[0],fitted_tail[-1].shape[0]])-1
                delaytime = int(min(max((np.abs((fitted_tail[-2][minlen,:]-fitted_tail[-1][minlen,:])**2).sum()**.5)**1.2*3-1,1), 500))
                # Question. why calculate delay time in a such trouble way?
            cv2.waitKey(delaytime)

        '''2-7. OUTPUT JPEG'''
        #task. temp omit
        if output_jpegs:
            if first_frame:
                jpegs_dir = pickdir()
                if not os.path.exists(jpegs_dir):
                    os.makedirs(jpegs_dir)
            jpg_out = Image.fromarray(frame_display)
            jpg_out.save(os.path.normpath(jpegs_dir +'\\'+ str(len(fitted_tail)-1)+'.jpg'))

        '''2-8. FALSE 1ST FRAME AND READ NEXT FRAME'''
        first_frame = False
        # cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,float(len(fitted_tail)) );  #workaround for raw videos crash, but massively (ie 5x) slower
        s, frame = cap.read()
        if s:     # Only process valid image frames
           frame = cv2.resize(frame, (0,0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)  #resize-tag #resize the frame!

        # turn off the first_frame and update the frame with next frame in video
        # cv2.VideoCapture.read([image]) returns tuple (retval, image), so frame only takes the returned image
    print "Done in %.2f seconds" % (time.time()-starttime)

    '''3RD PART. WARNING SYSTEM'''
    'DT-NOTE FOLLOWING IS LIKE WARNING SYSTEM, TEMPORARILLY SKIP THEM'
    fit_lengths = np.array([len(i) for i in fitted_tail])   ########tag########
    if np.std(fit_lengths) > 3 or plotlengths:
        print 'Abnormal variances in tail length detected, check results: ', filename
        pylab.plot(range(0,len(fitted_tail)),fit_lengths)
        pylab.ylim((0,5+max(fit_lengths)))
        pylab.xlabel("Frame")
        pylab.ylabel('Tail points')
        pylab.title('Tail fit lengths')
        print 'Close graph to continue!'
        pylab.show()

    if any(fit_lengths<25):
        print "Warning - short tail detected in some frames - min: ", min(fit_lengths)

    if len(fitted_tail) != int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)):
        print "Warning - number of frames processed doesn't match number of video frames - can happen with videos over 2gb!"
        print "Frames processed: " , len(fitted_tail)
        print "Actual frames according to video header: " , int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))

    '''4TH PART. DESTROYWINDOW AND RETURN!'''
    cv2.destroyAllWindows()
    return fitted_tail, first_point, start_point, direction, FPS, numframes, tailedges_threshold
    # Question. what is the function of returned value? simply just stored in shelf?

def tailfit_batch(video_list=[], display=True, displayonlyfirst = True,shelve_path = 'default.shv', startpoints=None, reuse_startpoint = False, tail_startpoint = None, tail_firstpoint = None, scale=0.5):

    shv=shelve.open(shelve_path,writeback=False)
    # Shelve has to be open in ord
    # shelve.open(), Open a persistent dictionary. The filename specified is the base filename for the underlying database.
    # If the optional writeback parameter is set to True, all entries accessed are also cached in memory, and written back on sync() and close()
    first = True

    for i, videopath in enumerate(video_list):
        if type(startpoints) is list:
            fittedtail, first_point, startpoint,  direction, FPS, numframes, tailedges_thresh  = tailfit(videopath,(first or not displayonlyfirst) and display ,startpoints[i], scale=scale)
        else:
            # in AVI situation, first time, startpoints is None.
            'DT-NOTE. THIS IS THE FUNCTION I REALLY NEED TO FOCUS ON!'
            fittedtail, first_point, startpoint, direction, FPS, numframes, tailedges_thresh  = tailfit(videopath,(first or not displayonlyfirst) and display ,startpoints, tail_startpoint = tail_startpoint, tail_firstpoint = tail_firstpoint, scale=scale)
            # tailfit function is used to analysis and display

            if reuse_startpoint:
                startpoints = [startpoint]*len(video_list)  #DT-new tag

        fittedtail = normalizetailfit(fittedtail)
        # tail_ampitude_list should stores the true value for tail movement

        '''STORE THE RESULT IN SHV AFTERING HASHING'''
        shahash = hashfile(open(videopath, 'rb'), hashlib.sha256())
        # open(), Open file and return a corresponding file object. If the file cannot be opened, an OSError is raised.

        '''RESULTS STORES INTO SHV/ITEMS IN SHV''' #TAG
        result =  tailfitresult(fittedtail, str(os.path.basename(videopath)),videopath, startpoint, FPS, len(fittedtail), direction, shahash, __version__)   #DT-tag
        shv[str(os.path.basename(videopath))]=result
        shv.sync()

        if first:
            first = False

    shv.close()
    return first_point, startpoint, tailedges_thresh


if __name__ == "__main__":
##    tail=tailfit('12-03-20.428.avi',display=1)
##    tail=tailfit(pickfile(),display=askyesno(text='Display frames?'),output_jpegs = 0)
##    tail=tailfit('test_tailfit.avi',display=1,output_jpegs = 0, start_point = [138, 176])
    print filenames
    # returned filenames is a tuple, eg. ("C:/DT files/Julie Semmelhack Lab/python learning/code/Joe's Tailfit - 0.9.3/example.avi",)

    '''PART-1 PICK THE FILE'''
    filenames = pickfiles(filetypes=[("AVI Video", ("*.avi",)), ("Shelve files", '*.shv'), ('All', '*')])  #DT-Customized code
    # folder = 'G:\DT-data\\2018\Jan\Jan 11th (high density)\\20180111_2nd_good\\temp\\temp'  # this should be the folder where you put all the videos for analysis
    # csv_filename = ''   # this should be the file where you stored the striking frame, give the fullname including the folder!
    # filenames = (folder + str(os.listdir(folder)[0]),)
    # print 'new filenames: ', filenames

    '''SITUATION NO.1 all the files are .shv'''
    if all([f.endswith('.shv') for f in filenames]):
        # all(iterable), Return True if all elements of the iterable are true (or if the iterable is not empty).
        # str.endswith(suffix[, start[, end]]), Return True if the string ends with the specified suffix, otherwise return False.
        output_suffix = ''
        for shvpath in [avi for avi in filenames if avi.endswith('.shv')]:
            shv = shelve.open(shvpath)
            # shv is the shelf that stores the content of opened .shv file
            # A "shelf" is a persistent, dictionary-like object. The difference with "dbm" databases is that the values (not the keys!) in a shelf can be essentially arbitrary Python objects - anything that the pickle module can handle.
            # This includes most class instances, recursive data types, and objects containing lots of shared sub-objects. The keys are ordinary strings.
            # As for database, The biggest difference between a database and a dictionary is that the database is on disk (or other permanent storage), so it persists after the program ends.
            # shelve.open(), Open a persistent dictionary. The filename specified is the base filename for the underlying database.
            basenames = shv.keys()
            # basenames would be a list stores the keys in shv shelf

            if type(shv[basenames[0]]) is tailfitresult:   #tag
                startpoints = [shv[j].startpoint for j in shv.keys()] #tag
                # shv is the shelf that stores the content of opened .shv file
                # Question. so startpoint should be defined within tailfitresult class?
            elif type(shv[basenames[0]]) is list:
                startpoints = [shv[j][1] for j in shv.keys()]
            else:
                raise Exception("Unknown tailfit format!")

            shv.close()

            print 'Running from: ', os.path.basename(shvpath)
            print 'Filenames: ', ' '.join(basenames)

            basedir = pickdir()
            # Question. choose the output directory? seems not, so why pick again
            # Answer. the 'second' pick directory here is to get the avi file
            avis = [os.path.join(basedir,avi) for avi in basenames]
            assert all([os.path.exists(avi) for avi in avis]), "Exiting, couldn't find matching avi file for all files!"
            # Question. the criteria for the picking directory

            outputshv = saveasfile(filetypes = [("Shelve files",'*.shv'), ('All','*') ],defaultextension='.shv')
            # Choose the output directory and edit the output shelve file name as well

            print "Running tailfit using shelve names and startpoints"
            # Question. what does startpoints means?

            '''MAJOR ANALYSIS FUNCTION'''  # when choosing the shv as the file...this is one of the situation. skip first
            tailfit_batch(avis,False,False,outputshv,startpoints=startpoints)    # TASK # dt-tag # do this later

    else:
        '''SITUATION NO.2 not all the files are .shv'''
        avis = [avi for avi in filenames if avi.endswith('.avi')]
        assert len(avis) == len(filenames), 'You need to select all only AVIs or all only shelve files'

        #outputshv = saveasfile(filetypes = [("Shelve files",'*.shv'), ('All','*') ],defaultextension='.shv')
        # outputshv eg. C:/DT files/ Semmelhack Lab/python learning/code/Joe's Tailfit - 0.9.3/test.shv
        #print outputshv

        #DT-customized outputshv, assumming only one avi in the folder
        #outputshv = folder + str(avis[0]) + '.shv'
        #print 'new ', outputshv

        display=askyesno(text='Display frames?')
        displayonlyfirst = True
        if display and len(avis)>1:
            displayonlyfirst=askyesno(text='Display only first video?')

        'MAJOR FUNCTION'
        tailfit_batch(avis,display,displayonlyfirst, reuse_startpoint = False) #this is where you change if you want to reuse the startpoint
        ######### output the default.shv in the code's folder!!!!!!
        # NOTE. tailfit_batch use tailfit function to analysis and display, it stores the result in hashed shelf.



