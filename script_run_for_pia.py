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
from utf_csv import UnicodeWriter

def rename_for_ease(vid_files, out_file_script = 'rename.sh'):
    commands = []
    
    # make destination dirs
    dirs = list(set([os.path.split(vid_file)[0] for vid_file in vid_files]))
    for file_curr in dirs:
        if ' ' not in file_curr:
            continue
        out_dir = file_curr.replace(' ','_')
        print file_curr, out_dir
        if not os.path.exists(out_dir):
            print out_dir
            command = ' '.join(['mkdir','--parents','"'+out_dir+'"',';'])
            commands.append(command)
        
    for file_curr in vid_files:
        if ' ' not in file_curr:
            continue
        out_file = file_curr.replace(' ','_')
        command = ' '.join(['mv','"'+file_curr+'"',out_file])
        commands.append(command)
        print len(commands)

    util.writeFile(out_file_script,commands)

def script_run_for_all(all_video_files):
    # dir_meta = '../pia_files'
    # all_video_files = []
    # for dir_level in ['*','*/*']:
    #     for ext in ['*.mp4','*.MP4']:
    #         all_video_files = all_video_files + glob.glob(os.path.join(dir_meta, dir_level, ext))
    temp_folder = '../temp_folder_lps'

    print len(all_video_files)
    log_file = 'log_lps.txt'
    logs = []
    for idx_video_file, video_file in enumerate(all_video_files):
        try:
            vid_file_new = os.path.join(temp_folder,os.path.split(video_file)[1])
            # print video_file
            # print temp_folder
            shutil.copy(video_file, temp_folder)

            gvr.main(vid_file_new,'all',5,True,'')
            frame_dir = vid_file_new[:vid_file_new.rindex('.')]+'_frames'
            assert os.path.exists(frame_dir)
            shutil.rmtree(frame_dir)
            os.remove(vid_file_new)

            command = ' '.join(['mv',vid_file_new[:vid_file_new.rindex('.')]+'*',os.path.split(video_file)[0]])
            src = vid_file_new[:vid_file_new.rindex('.')]+'_result_files'
            dst = os.path.split(video_file)[0]

            dst_file = os.path.join(dst,os.path.split(src)[1])
            # print dst_file
            if os.path.exists(dst_file):
                shutil.rmtree(dst_file)

            #run command
            # print src
            # print dst
            shutil.move(src,dst)
        


            # gvr.main(video_file,'all',5,True,'')
            # frame_dir = video_file[:video_file.rindex('.')]+'_frames'
            # assert os.path.exists(frame_dir)
            # shutil.rmtree(frame_dir)
            str_log = 'completed '+video_file
            # break
        except:
            str_log = 'PROBLEM '+video_file
        print idx_video_file, str_log
        logs.append(str_log)
        util.writeFile(log_file,logs)
    
    

def script_collate_responses():
    dir_meta = '../data/pia_plots'
    dirs = []
    for dir_level in ['*_result_files','*/*_result_files','*/*/*_result_files']:
        dirs += [dir_curr for dir_curr in glob.glob(os.path.join(dir_meta,dir_level)) if os.path.isdir(dir_curr)]

    for idx_dir_curr, dir_curr in enumerate(dirs):
        print idx_dir_curr,len(dirs)
        text_files = glob.glob(os.path.join(dir_curr,'*[0-9].txt'))
        text_files.sort()
        front_file = os.path.join(dir_curr,'front_dets.txt')
        side_file = os.path.join(dir_curr,'side_dets.txt')
        front_lines = []
        side_lines = []
        for text_file in text_files:
            lines = util.readLinesFromFile(text_file)
            front_lines_curr = 0.
            side_lines_curr = 0.
            if len(lines)>0:
                det_confs = [[int(line.split(' ')[0]),float(line.split(' ')[1])] for line in lines]
                det_confs = np.array(det_confs)
                if np.sum(det_confs[:,0]==0)>0:
                    side_lines_curr = np.max(det_confs[det_confs[:,0]==0,1])
                if np.sum(det_confs[:,0]==1)>0:
                    front_lines_curr = np.max(det_confs[det_confs[:,0]==1,1])
            
            front_lines.append(front_lines_curr)
            side_lines.append(side_lines_curr)
        side_lines = ['%.2f' % val for val in side_lines]
        front_lines = ['%.2f' % val for val in front_lines]
        util.writeFile(front_file,front_lines)
        util.writeFile(side_file,side_lines)


def script_write_giant_csv():
    dir_meta = '../data/pia_plots'
    dirs = []
    for dir_level in ['*_result_files','*/*_result_files','*/*/*_result_files']:
        dirs += [dir_curr for dir_curr in glob.glob(os.path.join(dir_meta,dir_level)) if os.path.isdir(dir_curr)]

    # print len(dirs)
    # return
    out_file_side = os.path.join(dir_meta,'side_detections.csv')
    out_file_front = os.path.join(dir_meta,'front_detections.csv')
    side_rows = []
    front_rows = []

    for idx_dir_curr, dir_curr in enumerate(dirs):
        for rows_all,file_curr in [(side_rows,'side_dets.txt'),(front_rows,'front_dets.txt')]:
            row_curr = []

            row_curr.append(dir_curr.replace('_result_files','').replace(dir_meta+'/',''))
            row_curr += util.readLinesFromFile(os.path.join(dir_curr,file_curr))
            rows_all.append(row_curr)
    print len(side_rows),side_rows[0]
    print len(front_rows),front_rows[0]

    import csv
    
    for rows,file_name in [(side_rows, out_file_side),(front_rows, out_file_front)]:
        with open(file_name,'w+') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(rows)



def get_all_files(meta_dir, post_file = '*.mp4'):
    # /*'
    meta_dir = os.path.join(meta_dir,'*','*')
    post_file = '*.MP4'

    dirs_all = util.getAllSubDirectories(meta_dir)
    # [dir_curr for dir_curr in glob.glob(meta_dir) if os.path.isdir(dir_curr)]
    # 
    print len(dirs_all)

    vid_files = []
    for dir_curr in dirs_all:
        # print dir_curr
        vid_files += glob.glob(os.path.join(dir_curr,post_file))
    
    # print len(vid_files)
    return vid_files


def scripts_in_main_may_use():
    out_dir = '../data/pia_plots'
    to_replace = '.'
    util.mkdir(out_dir)
    dir_meta = '../pia_files'
    all_video_files = []
    for dir_level in ['*','*/*']:
        for ext in ['*.mp4','*.MP4']:
            all_video_files = all_video_files + glob.glob(os.path.join(dir_meta, dir_level, ext))

    print len(all_video_files)
    return
    im_paths = []
    captions = []
    out_file_html = os.path.join(out_dir,'all_plots.html')
    for video_file in all_video_files:
        frame_dir = video_file[:video_file.rindex('.')]+'_result_files'
        assert os.path.exists(frame_dir)
        out_dir_curr = frame_dir.replace(dir_meta,out_dir)
        # shutil.copytree(frame_dir,out_dir_curr)

        im_path = os.path.join(out_dir_curr,'detections_over_time.jpg').replace(out_dir,'')[1:]
        print 'out_dir',out_dir
        print os.path.join(out_dir,im_path)
        assert os.path.exists(os.path.join(out_dir,im_path))
        # [1:]
        print im_path
        # raw_input()
        # foo.encode('utf8')
        im_paths.append([im_path.decode('utf-8').strip()])
        captions.append([frame_dir.decode('utf-8').strip()])

    im_paths = [['test/detections_over_time.jpg']]+im_paths
    captions = [['test']]+captions
    visualize.writeHTML(out_file_html,im_paths,captions,455,570)

def main():
    meta_dir = '../pia'
    # /filmer_forsok/Danmark_-18'
    # vid_files = get_all_files(meta_dir)
    # rename_for_ease (vid_files)
    vid_files = get_all_files(meta_dir)

    # return
    done = []
    not_done = []
    for vid_file in vid_files:
        if 'RECYCLE' in vid_file:
            continue
        # print vid_file
        result_file = os.path.join(vid_file[:vid_file.rindex('.')]+'_result_files','detections_over_time.jpg')
        if os.path.exists(result_file):
            done.append(vid_file)
        else:
            not_done.append(vid_file)

    print 'done',len(done)
    print 'not_done',len(not_done)
    
    # rename_for_ease(not_done)

    # for nd in not_done:
    #     print nd
    #     raw_input()
    not_done = not_done[268:]
    script_run_for_all(not_done)

    # script_collate_responses()
    # script_write_giant_csv()
    # return













if __name__=='__main__':
    main()