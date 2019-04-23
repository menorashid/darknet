import os
import sys
from helpers import util
from helpers.gui import Gui
import numpy as np
import glob


def get_res_path(vid_file):
    return vid_file[:vid_file.rindex('.')]+'_result_files'



def collate_results_for_plotting(res_dir, fps =5):
    vid_name = os.path.split(res_dir.replace('_result_files',''))[1]
    text_files = glob.glob(os.path.join(res_dir,vid_name+'_*[0-9].txt'))
    text_files.sort()

    det_confs =[[],[]]
    boxes = [[],[]]
    time =[]    
    for text_file in text_files:
        num = os.path.split(text_file)[1]
        num = int(num[num.rindex('_')+1:num.rindex('.')])-1
        sec = fps*num +fps/2.
        
        time.append(sec)

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
    time = np.array(time)

    return det_confs, time, boxes

    

def main():
    # gui.dummy()

    # return
    vid_path = '../data/Cisi_kortsida.MP4'
    res_dir = get_res_path(vid_path)
    fps = 5
    size_output = [416,416]
    smooth = True
    det_confs, time, boxes = collate_results_for_plotting(res_dir, fps)


    det_confs_plot = [[],[]]

    if smooth:
        for idx, det in enumerate(det_confs):
            smooth_window = min(int(round(60/float(fps))),len(det))
            box = np.ones((smooth_window,))/float(smooth_window)
            det_confs_plot[idx] = np.convolve(np.array(det), box, mode='same') 
    
    vals = [(time, val) for val in det_confs]
    smooth_vals = [(time, val) for val in det_confs_plot]
    gui = Gui(vals, smooth_vals, vid_path, boxes = boxes, fps = fps, size_output = size_output)

    # [det_confs[0],det_confs[1],det_confs_plot[0],det_confs_plot[1]]]

    # labels = ['Side','Front','Side Smooth','Front Smooth']
    # xlabel = 'Video Time (min)'
    # ylabel = 'Detection Confidence'
    # title = 'Face Detections Over Time'
    # # out_file = os.path.join(out_dir,'detections_over_time.jpg')
    # out_file = None


    # xAndYs = [(time, val) for val in [det_confs[0],det_confs[1],det_confs_plot[0],det_confs_plot[1]]]
    # colors = ['C0','C1','C0','C1']
    # alphas = [0.5,0.5,1.,1.]
    # markers = ['o']*4
    # markersize = [2]*4
    # colors_etc = [colors, alphas, markers, markersize]

    # gui.plotSimple(xAndYs,out_file = out_file,xlabel = xlabel,ylabel = ylabel,title = title, legend_entries = labels, colors_etc = colors_etc)
    # print 'DETECTION GRAPH:', out_file

    # wait()
    raw_input()
    # while gui.fig:
    #     print gui.fig.number
        

    # vid_name = os.path.split(vid_path)[1]
    # vid_name = vid_name[:vid_name.rindex('.')]
    # print vid_name

    # text_files = glob.glob(os.path.join(res_dir,vid_name+'_*[0-9].txt'))
    # text_files.sort()
    # print len(text_files)



        

    # collate_results_for_plotting



if __name__=='__main__':
    main()