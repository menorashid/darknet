import os
import sys
from helpers import util, visualize
import numpy as np
import scipy.misc
import cv2
import glob
import argparse
import subprocess

def test_frames(out_dir,data_dir):
    in_data_file = 'horse_face/side_horse_face_video_template.data'
    config_file = 'horse_face/yolo_two_class.cfg'
    model_file = '../experiments/yolo_side_horse_wframes/yolo_two_class_2000.weights'

    
    test_images = glob.glob(os.path.join(data_dir,'*.jpg'))
    test_images.sort()
    test_file = os.path.join(out_dir,'test_images.txt')
    util.writeFile(test_file,test_images)
    
    # result_log_file = os.path.join(out_dir,'result_log.txt')
    out_data_file = os.path.join(out_dir,'side_horse_face.data')


    with open(in_data_file,'rb') as f:
        lines=f.read();
    
    lines = lines.replace('$RESULT$',out_dir)
    lines = lines.replace('$DATA$',data_dir)
    
    with open(out_data_file,'wb') as f:
        f.write(lines);

    command = []
    command.extend(['./darknet','detector','test_bbox'])
    command.append(out_data_file)
    command.append(config_file)
    command.append(model_file)
    command.extend(['<',test_file])
        # ,'>'])
    # command.append(result_log_file)
    command.extend(['-thresh','0.2'])
    command = ' '.join(command)
    print command
    subprocess.call(command, shell=True)

    

def extract_frames(video_file,data_dir,fps,size_output):
    # ffmpeg -i ../data/Surveillance/ch06_20161212115301.mp4 -vf fps=1/5 -s 416x416 ../data/Surveillance/ch06_20161212115301/ch06_20161212115301_%09d.jpg -hide_banner 
    
    video_name = os.path.split(video_file)[1]
    video_name = video_name[:video_name.rindex('.')]

    out_file_format = os.path.join(data_dir,video_name+'_%09d.jpg')

    command = []
    command.extend(['ffmpeg','-i',video_file])
    command.extend(['-vf','fps=1/'+str(fps)])
    command.extend(['-s',str(size_output[0])+'x'+str(size_output[1])])
    command.append(out_file_format)
    command.append('-hide_banner')
    command = ' '.join(command)
    
    print command
    subprocess.call(command, shell=True)
    

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
        smooth_window = int(round(60/float(fps)))
        # print smooth_window

        for idx, det in enumerate(det_confs):
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
        subprocess.call('rm '+os.path.join(data_dir,'*.jpg'),shell=True)
        extract_frames(video_file,data_dir,fps,size_output)
        visualize.writeHTMLForFolder(data_dir)
        print 'DONE EXTRACTING FRAMES'

    if to_run=='all' or to_run=='test':
        print 'TESTING FRAMES'
        test_frames(out_dir,data_dir)
        print 'DONE TESTING'

    if to_run=='all' or to_run=='graph':
        print 'PLOTTING DETECTIONS OVER TIME'
        plot_detections_over_time(data_dir,out_dir,fps,smooth)

    if to_run=='plot':
        plot_detections(data_dir,out_dir)


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Process horse videos.')
    parser.add_argument('-video', dest = 'video_file',type=str, default='', required = True,help='input video')
    parser.add_argument('-sec', dest= 'sec',type=int, default=5, help='seconds per frame. default 1 frame every 5 seconds')
    parser.add_argument('-action', dest = 'to_run',type=str, default='all', help="what to do with video. 'all' extracts frames, tests them and then plots a graph of detections.")
    parser.add_argument('-smooth', dest = 'smooth', default=True, action = 'store_true',help='plot detections over time with smoothing per minute.default is False')
    parser.add_argument('-dirpost', dest = 'post_dir', type=str, default='', help="a string to post pend to all created folders")
    
    args = parser.parse_args()
    main(args.video_file,args.to_run,args.sec,args.smooth,args.post_dir)











