import os
import sys
from helpers import util, visualize
import numpy as np
import scipy.misc
import csv
import datetime
import re

def main():
    npz_file = '../data/Aslan/2018-12-23/ch02_20181223162441_result_files/results_collated.npz'

    res_dir = '../data/Aslan/2018-12-23/ch02_20181223130000_result_files'
    vid_name = 'ch02_20181223130000'
    command = 'rm '+'"'+os.path.join(res_dir,vid_name+'"_*[0-9].txt')
    command = 'rm '+'"'+os.path.join(res_dir,'results_collated."*')
    command = 'rm '+'"'+os.path.join(res_dir,'detections_over_time.jpg"')
    print command
    import subprocess
    subprocess.call(command, shell = True)

    # subprocess.call('rm '+'"'+os.path.join(res_dir,vid_name+'"_*[0-9].txt'),shell=True)
    # subprocess.call('ls '+'"'+os.path.join(res_dir,vid_name+'"_*[0-9].txt'),shell=True)
    # subprocess.call('rm '+'"'+os.path.join(res_dir,'results_collated.*'),shell=True)


    # print npz_file
    # out_file_csv = npz_file.replace('.npz','.txt')
    # loaded = np.load(npz_file)
    # det_confs = loaded['det_confs']
    # times = loaded['times']
    # boxes = loaded['boxes']
    # vid_name = 'ch02_20181223162441'

    
    # str_dig = '[0-9]'
    # str_reg = 'ch'+str_dig*2+'_'+str_dig*14
    # vid_start_time = None

    # if re.match(str_reg, vid_name):
    #     cam_time = vid_name.split('_')[1]        
    #     try:
    #         vid_start_time = datetime.datetime.strptime(cam_time,'%Y%m%d%H%M%S')
    #     except:
    #         vid_start_time = None
    
    # with open(out_file_csv, 'w') as csvfile:
    #     writer = csv.writer(csvfile)
    #     row = []
    #     if vid_start_time is not None:
    #         row.append('Absolute Time')
    #     row += ['Video Time','Side Detection Confidence', 'Front Detection Confidence','Side Box', 'Front Box']
        
    #     writer.writerow(row)
    #     for idx_det in range(len(times)):
    #         row = []
    #         time_curr = datetime.timedelta(seconds = times[idx_det]) 
    #         if vid_start_time is not None:
    #             time_added = vid_start_time+time_curr
    #             row.append(time_added.strftime('%H:%M:%S.%f'))

    #         row.append(str(time_curr))
    #         row.append(str(det_confs[0][idx_det]))
    #         row.append(str(det_confs[1][idx_det]))
    #         row.append(str(boxes[0][idx_det]))
    #         row.append(str(boxes[1][idx_det]))
    #         writer.writerow(row)
            


    



if __name__=='__main__':
    main()


# Brava/2018-11-03/:
# ch02_20181103000000.mp4

