import os
import sys
from helpers import util, visualize
import numpy as np
import scipy.misc
import csv
import glob
import argparse
import subprocess
import datetime
import time
import matplotlib.pyplot as plt
import re

def test_frames(out_dir,data_dir, no_out = False):
    in_data_file = 'horse_face/side_horse_face_video_template.data'
    config_file = 'horse_face/yolo_two_class.cfg'
    model_file = 'model/yolo_two_class_2000.weights'
    # '../experiments/yolo_side_horse_wframes/yolo_two_class_2000.weights'

    
    test_images = glob.glob(os.path.join(data_dir,'*.jpg'))
    test_images.sort()
    test_file = os.path.join(out_dir,'test_images.txt')
    util.writeFile(test_file,test_images)
    
    # result_log_file = os.path.join(out_dir,'result_log.txt')
    out_data_file = os.path.join(out_dir,'side_horse_face.data')


    with open(in_data_file,'rb') as f:
        lines=f.read();
    
    # print lines
    lines = lines.replace('$RESULT$',out_dir)
    lines = lines.replace('$DATA$',data_dir)
    
    with open(out_data_file,'wb') as f:
        f.write(lines);

    command = []
    command.extend(['./darknet','detector','test_bbox'])
    command.append(out_data_file)
    command.append(config_file)
    command.append(model_file)
    command.extend(['<','"'+test_file+'"'])
        # ,'>'])
    # command.append(result_log_file)
    command.extend(['-thresh','0.2'])
    if no_out:
        command.append('> /dev/null 2>&1')

    command = ' '.join(command)
    print command
    for num_im, im in enumerate(test_images):
        out_file = os.path.join(out_dir,os.path.split(im)[1].replace('.jpg','.txt'))
        util.writeFile(out_file,command)
        if num_im%10==0:
            time.sleep(3)
    subprocess.call(command, shell=True)

def test_frames_gui((out_dir,data_dir, no_out)):
    in_data_file = 'horse_face/side_horse_face_video_template.data'
    config_file = 'horse_face/yolo_two_class.cfg'
    model_file = 'model/yolo_two_class_2000.weights'
    # '../experiments/yolo_side_horse_wframes/yolo_two_class_2000.weights'

    
    test_images = glob.glob(os.path.join(data_dir,'*.jpg'))
    test_images.sort()
    test_file = os.path.join(out_dir,'test_images.txt')
    util.writeFile(test_file,test_images)
    
    # result_log_file = os.path.join(out_dir,'result_log.txt')
    out_data_file = os.path.join(out_dir,'side_horse_face.data')


    with open(in_data_file,'rb') as f:
        lines=f.read();
    
    # print lines
    lines = lines.replace('$RESULT$',out_dir)
    lines = lines.replace('$DATA$',data_dir)
    
    with open(out_data_file,'wb') as f:
        f.write(lines);

    command = []
    command.extend(['./darknet','detector','test_bbox'])
    command.append('"'+out_data_file+'"')
    command.append(config_file)
    command.append(model_file)
    command.extend(['<','"'+test_file+'"'])
        # ,'>'])
    # command.append(result_log_file)
    command.extend(['-thresh','0.2'])
    if no_out:
        command.append('> /dev/null 2>&1')

    command = ' '.join(command)
    print command
    # for num_im, im in enumerate(test_images):
    #     out_file = os.path.join(out_dir,os.path.split(im)[1].replace('.jpg','.txt'))
    #     util.writeFile(out_file,command)
    #     if num_im%10==0:
    #         time.sleep(1)
    subprocess.call(command, shell=True)


def run_commandlines(command):
    # print command
    command = command+'> /dev/null 2>&1'
    # print command
    subprocess.call(command, shell=True)


def get_duration(video_file):

    command = ['ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1']
    command.append('"'+video_file+'"')
    command = ' '.join(command)
    secs = subprocess.check_output(command, shell = True)
    secs = float(secs)
    return secs

def extract_frames(video_file,data_dir,fps,size_output):
    # ffmpeg -i ../data/Surveillance/ch06_20161212115301.mp4 -vf fps=1/5 -s 416x416 ../data/Surveillance/ch06_20161212115301/ch06_20161212115301_%09d.jpg -hide_banner 
    
    video_name = os.path.split(video_file)[1]
    video_name = video_name[:video_name.rindex('.')]

    out_file_format = os.path.join(data_dir,video_name+'_%09d.jpg')

    command = []
    command.extend(['ffmpeg','-i','"'+video_file+'"'])
    command.extend(['-vf','fps=1/'+str(fps)])
    command.extend(['-s',str(size_output[0])+'x'+str(size_output[1])])
    command.append('"'+out_file_format+'"')
    command.append('-hide_banner')
    # command.append('&> temp')
    command = ' '.join(command)
    
    print command
    subprocess.call(command, shell=True)
    


def collate_results_for_plotting(vid_name, res_dir, fps =5):
    # vid_name = os.path.split(res_dir.replace('_result_files',''))[1]
    print 'vid_name',vid_name

    out_file = os.path.join(res_dir, 'results_collated.npz')
    out_file_csv = os.path.join(res_dir, 'results_collated.csv')
    if os.path.exists(out_file):
        loaded = np.load(out_file)
        det_confs = loaded['det_confs']
        times = loaded['times']
        boxes = loaded['boxes']
    else:
        text_files = glob.glob(os.path.join(res_dir,vid_name+'_*[0-9].txt'))
        text_files.sort()

        print len(text_files)
        
        det_confs =[[],[]]
        boxes = [[],[]]
        times =[]    
        for text_file in text_files:
            num = os.path.split(text_file)[1]
            num = int(num[num.rindex('_')+1:num.rindex('.')])-1
            sec = fps*num +fps/2.
            
            times.append(sec)

            dets = util.readLinesFromFile(text_file)
            if len(dets)==0:
                [det_confs[idx].append(0) for idx in range(2)]
                [boxes[idx].append(-1*np.ones((1,4))) for idx in range(2)]
            else:
                
                class_conf = []
                boxes_curr = []
                for det in dets:
                    det = det.split(' ')
                    box_curr = np.array([int(val) for val in det[2:]])
                    det = [int(det[0]),float(det[1])]
                    boxes_curr.append(box_curr)
                    class_conf.append(det)

                
                class_conf = np.array(class_conf)
                for class_curr in range(2):
                    rel_idx = np.where(class_conf[:,0]==class_curr)[0]
                    rel_dets = class_conf[rel_idx,:]
                    
                    if rel_dets.size ==0:
                        max_conf=0
                        box_max = -1*np.ones((1,4))

                    else:
                        max_conf = np.max(rel_dets[:,1])
                        max_idx = rel_idx[np.argmax(rel_dets[:,1])]
                        box_max = boxes_curr[max_idx][np.newaxis,:]

                    det_confs[class_curr].append(max_conf)
                    boxes[class_curr].append(box_max)
        
        det_confs = np.array(det_confs)
        boxes = np.array([np.concatenate(boxes[idx], axis =0) for idx in range(len(boxes))])
        times = np.array(times)
        # print out_file
        write_detections_csv(out_file_csv, vid_name, det_confs, boxes, times)

        np.savez(out_file, det_confs = det_confs, boxes = boxes, times = times)
    
    return det_confs, times, boxes

def write_detections_csv(out_file_csv, vid_name, det_confs, boxes, times):
    str_dig = '[0-9]'
    str_reg = 'ch'+str_dig*2+'_'+str_dig*14
    vid_start_time = None

    if re.match(str_reg, vid_name):
        cam_time = vid_name.split('_')[1]        
        try:
            vid_start_time = datetime.datetime.strptime(cam_time,'%Y%m%d%H%M%S')
        except:
            vid_start_time = None
    
    with open(out_file_csv, 'w') as csvfile:
        writer = csv.writer(csvfile)
        row = []
        if vid_start_time is not None:
            row.append('Absolute Time')
        row += ['Video Time','Side Detection Confidence', 'Front Detection Confidence','Side Box', 'Front Box']
        
        writer.writerow(row)
        for idx_det in range(len(times)):
            row = []
            time_curr = datetime.timedelta(seconds = times[idx_det]) 
            if vid_start_time is not None:
                time_added = vid_start_time+time_curr
                row.append(time_added.strftime('%H:%M:%S.%f'))
                
            row.append(str(time_curr))
            row.append(str(det_confs[0][idx_det]))
            row.append(str(det_confs[1][idx_det]))
            row.append(str(boxes[0][idx_det]))
            row.append(str(boxes[1][idx_det]))
            writer.writerow(row)



def plot_detections_over_time_new(vid_name, res_dir, fps):
    det_confs, times, boxes = collate_results_for_plotting(vid_name, res_dir, fps)
    xAndYs, colors_etc, labels, title, legend_entries = util.get_all_plotting_vals(det_confs, times, boxes,fps)

    # xAndYs = smoothvals+vals
    xAndYs = [(val_curr[0]/60.,val_curr[1]) for val_curr in xAndYs]
    out_file = os.path.join(res_dir, 'detections_over_time.jpg')

    visualize.plotSimple(xAndYs, out_file, title = title , xlabel = labels[0], ylabel =labels[1],legend_entries = legend_entries, colors_etc = colors_etc)
    
    return out_file


def plot_detections_over_time(data_dir,out_dir,fps,smooth=False):

    frame_files = glob.glob(os.path.join(data_dir,'*.jpg'))
    frame_files.sort()
    result_files = [file.replace(data_dir,out_dir).replace('.jpg','.txt') for file in frame_files]

    det_confs =[ [],[]]
    time =[]    
    for frame,result in zip(frame_files,result_files):
        num = fps*(int(frame[frame.rindex('_')+1:frame.rindex('.')])-1)+fps/2.
        time.append(num/60.)
        # time.append(int(frame[frame.rindex('_')+1:frame.rindex('.')]))
        dets = util.readLinesFromFile(result)
        if len(dets)==0:
            [det_confs[idx].append(0) for idx in range(2)]
        else:
            class_conf = []
            for det in dets:
                det = det.split(' ')
                det = [int(det[0]),float(det[1])]
                class_conf.append(det)
            class_conf = np.array(class_conf)
            for class_curr in range(2):
                rel_dets = class_conf[class_conf[:,0]==class_curr,:]
                
                if rel_dets.size ==0:
                    max_conf=0
                else:
                    max_conf = np.max(rel_dets[:,1])
                det_confs[class_curr].append(max_conf)

    if smooth:
        
        for idx, det in enumerate(det_confs):
            smooth_window = min(int(round(60/float(fps))),len(det))
            box = np.ones((smooth_window,))/float(smooth_window)
            det_confs[idx] = np.convolve(np.array(det), box, mode='same') 
        
    labels = ['side','front']
    xlabel = 'Video Time (min)'
    ylabel = 'Detection Confidence'
    title = 'Face Detections Over Time'
    out_file = os.path.join(out_dir,'detections_over_time.jpg')
    visualize.plotSimple([(time,det_confs[0]),(time,det_confs[1])],out_file = out_file,xlabel = xlabel,ylabel = ylabel,title = title, legend_entries = labels)
    print 'DETECTION GRAPH:', out_file

def plot_detections(data_dir,out_dir):
    frame_files = glob.glob(os.path.join(data_dir,'*.jpg'))
    print len(frame_files)
    frame_files.sort()
    result_files = [file.replace(data_dir,out_dir).replace('.jpg','.txt') for file in frame_files]

    colors = [(255,0,255),(0,255,0)]
    for frame_file, result_file in zip(frame_files,result_files):
        out_file = result_file[:result_file.rindex('.')]+'.jpg'
        im = cv2.imread(frame_file)
        dets = util.readLinesFromFile(result_file)
        for det in dets:
            det = det.split(' ')
            class_curr = int(det[0])
            box = [int(val) for val in det[2:]]
            color = colors[class_curr]
            im = cv2.rectangle(im,(box[0],box[2]),(box[1],box[3]),color,5)
        cv2.imwrite(out_file,im)
    visualize.writeHTMLForFolder(out_dir)


def main(video_file,to_run,fps,smooth,post_dir):
    print video_file
    print 'to_run',to_run
    print 'sec',fps
    
    # video_file = '../data/Surveillance/ch02_20161212115300.mp4'
    out_dir = video_file[:video_file.rindex('.')]+'_result_files'+post_dir
    data_dir = video_file[:video_file.rindex('.')]+'_frames'+post_dir
    util.mkdir(data_dir)
    util.mkdir(out_dir)

    # fps = 5 #extract one frame every n seconds
    size_output = [416,416]

    if to_run=='all' or to_run=='extract':
        print 'EXTRACTING FRAMES'
        subprocess.call('rm '+'"'+os.path.join(data_dir,'*.jpg')+'"',shell=True)
        extract_frames(video_file,data_dir,fps,size_output)
        visualize.writeHTMLForFolder(data_dir)
        print 'DONE EXTRACTING FRAMES'

    # t = time.time()
    if to_run=='all' or to_run=='test':
        print 'TESTING FRAMES'
        test_frames(out_dir,data_dir)
        print 'DONE TESTING'

    if to_run=='all' or to_run=='graph':
        print 'PLOTTING DETECTIONS OVER TIME'
        plot_detections_over_time(data_dir,out_dir,fps,smooth)
    
    # print time.time()-t

    if to_run=='plot':
        print data_dir
        plot_detections(data_dir,out_dir)


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Process horse videos.')
    parser.add_argument('-video', dest = 'video_file',type=str, default='', required = True,help='input video')
    parser.add_argument('-sec', dest= 'sec',type=int, default=5, help='seconds per frame. default 1 frame every 5 seconds')
    parser.add_argument('-action', dest = 'to_run',type=str, default='all', help="what to do with video. 'all' extracts frames, tests them and then plots a graph of detections.")
    parser.add_argument('-smooth', dest = 'smooth', default=True, action = 'store_true',help='plot detections over time with smoothing per minute.default is True')
    parser.add_argument('-dirpost', dest = 'post_dir', type=str, default='', help="a string to post pend to all created folders")
    
    args = parser.parse_args()
    main(args.video_file,args.to_run,args.sec,args.smooth,args.post_dir)











