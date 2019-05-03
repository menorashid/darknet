import os
import sys
from helpers import util, visualize
import numpy as np
import scipy.misc
import cv2
import glob
import argparse
import subprocess
import time
import get_video_results as gvr
import shutil
import random
import csv
import multiprocessing


def get_count(vid_files):
    surv = 0
    other = 0
    for file_curr in vid_files:
        if 'surveillance' in file_curr.lower():
            surv+=1
        else:
            other+=1

    return surv, other

def choose_a_subset():
     #  read the video list
    file_list_txt = 'list_of_all_files.txt'
    vid_files = util.readLinesFromFile(file_list_txt)
    surv, other = get_count(vid_files)
    print len(vid_files)
    print surv, other
    random.shuffle(vid_files)

    #   randomly select a subset of videos
    vid_files = vid_files[:300]
    surv, other = get_count(vid_files)
    print len(vid_files)
    print surv, other

    #   see if filenames are unique
    just_vids = []
    out_dir = '../data_subset'
    util.mkdir(out_dir)

    lines_to_write = []
    for idx_file_curr, file_curr in enumerate(vid_files):    
        vid_name = os.path.split(file_curr)[1]
        vid_name = vid_name[:vid_name.rindex('.')]+'_'+str(idx_file_curr)+vid_name[vid_name.rindex('.'):]

        out_file = os.path.join(out_dir,vid_name )
        # print vid_name
        just_vids.append(out_file)

        line_curr = ' '.join(['cp',file_curr,out_file])
        lines_to_write.append(line_curr)


    print len(just_vids), len(set(just_vids))

    out_file = 'list_of_subset_files.txt'
    util.writeFile(out_file,lines_to_write)


def do_everything_horse_finder(vid_file,  fps = 5):

    tot_t = time.time()
    dir_pre = vid_file[:vid_file.rindex('.')]
    out_dir = dir_pre+'_result_files'
    frame_dir = dir_pre+'_frames'
    vid_name = os.path.split(vid_file)[1]
    vid_name = vid_name[:vid_name.rindex('.')]
    out_file_time = dir_pre+'_time.txt'
    # if os.path.exists(os.path.join(out_dir,'detections_over_time.jpg')):
    #     # print 'returning'
    #     return

    util.mkdir(out_dir)
    util.mkdir(frame_dir)

    # get vid length
    secs = gvr.get_duration(vid_file)
    inc_frames = fps/2.
    frame_times = list(np.arange(inc_frames, secs, fps))
    if (frame_times[-1]+fps)<secs:
        frame_times.append(frame_times[-1]+fps)

    commands = []
    for idx_time_curr,time_curr in enumerate(frame_times):
        commands.append( util.get_extract_image_command(vid_file, frame_dir, time_curr, idx_time_curr+1))

    # print commands[0]

    # extract frames mp and time it
    pool = multiprocessing.Pool()
    ext_t = time.time()
    pool.map(gvr.run_commandlines, commands)
    ext_t = time.time()-ext_t
    pool.close()
    pool.join()

    # run det and time it
    det_t = time.time()
    gvr.test_frames_gui((out_dir,frame_dir,True))
    det_t = time.time()-det_t

    
    plot_t = time.time()
    out_file_plot = gvr.plot_detections_over_time_new(vid_name, out_dir, fps)  
    plot_t = time.time()-plot_t

    tot_t = time.time()-tot_t

    # 834.72 7.27549290657 4.19708919525 0.20227599144 11.8656108379
    str_print = ' '.join(['%.2f'%val for val in [secs,ext_t,det_t,plot_t,tot_t]])
    util.writeFile(out_file_time,[str_print])


def copy_files():

    file_list_txt = 'list_of_subset_files.txt'
    commands = util.readLinesFromFile(file_list_txt)

    pool = multiprocessing.Pool()
    commands_new = []
    for command in commands:
        out_file = command.split(' ')[-1]
        if not os.path.exists(out_file):
            commands_new.append(command)

    print len(commands_new)
    pool.map(gvr.run_commandlines, commands_new)

def collate_times(out_dir):
    time_files = glob.glob(os.path.join(out_dir,'*_time.txt'))
    all_vals = []

    for time_file in time_files:
        vals = util.readLinesFromFile(time_file)[0]
        vals = [float(val) for val in vals.split(' ')]
        all_vals.append(vals)

    all_vals = np.array(all_vals)
    bin_keep = all_vals[:,0]>=300
    all_vals = all_vals[bin_keep,:]
    print all_vals.shape
    print 'sum',[util.convert_sec_to_str(val) for val in np.sum(all_vals,axis = 0)]
    time_files = np.array(time_files)
    time_files = time_files[bin_keep]
    # surv,other = get_count(time_files)
    # print surv, other

    print 'min',util.convert_sec_to_str(np.min(all_vals[:,0]))
    print 'max',util.convert_sec_to_str(np.max(all_vals[:,0]))
    print 'mean',util.convert_sec_to_str(np.mean(all_vals[:,0]))


    time_min = all_vals[:,0]/60.
    # print np.sum(time_min>10)
    # time_min[time_min<1]=1

    p_s_times = all_vals[:,1:]/time_min[:,np.newaxis]

    # bin_keep = time_min[:,0]>1
    # p_s_times = p_s_times[bin_keep,:]
    # time_min = time_min[bin_keep,:]

    idx_sort = np.argsort(time_min)
    time_min_sort = time_min[idx_sort]
    xAndYs = [(time_min_sort,p_s_times[idx_sort,idx]) for idx in range(p_s_times.shape[1])]
    out_file = '../data_subset/p_s_times.jpg'
    title = 'Time taken per task'
    legend_entries = ['Extraction','Detection','Plotting','Total']
    xlabel = 'Video Duration (min)'
    ylabel = 'Seconds Per Video Minute'
    visualize.plotSimple(xAndYs, out_file, title, xlabel, ylabel, legend_entries)
    print out_file
    # /(all_vals[:,:1]/60.)
    # print p_s_times[:10,:]
    # print all_vals[:10,:]
    print 'min',p_s_times[idx_sort[-1],:]
    print 'max',p_s_times[idx_sort[0],:]
    print 'mean',np.mean(p_s_times,axis = 0)
    # print np.median(p_s_times,axis = 0)
    print 'std',np.std(p_s_times,axis = 0)




def main():
    out_dir = '../data_subset'
    collate_times(out_dir)

    # copy_files()
    return
    # vid_files = 
    # pool = multiprocessing.Pool()
    # vid_file = '../data/Cisi_kortsida.MP4'

    file_list_txt = 'list_of_subset_files.txt'
    commands = util.readLinesFromFile(file_list_txt)
    
    vid_files = []    
    for command in commands:
        vid_file = command.split(' ')[-1]
        out_file_det = os.path.join(vid_file[:vid_file.rindex('.')]+'_result_files','detections_over_time.jpg')
        if not os.path.exists(out_file_det):
            vid_files.append(vid_file)

    print len(vid_files)

    for idx_vid_file,vid_file in enumerate(vid_files):
        print vid_file,idx_vid_file,len(vid_files)        
        try:
            do_everything_horse_finder(vid_file, fps = 5)
        except:
            print 'ERROR',vid_file, idx_vid_file





    #   copy them to folder
    #   for each file set up a text file that records time for each task



    

if __name__=='__main__':
    main()