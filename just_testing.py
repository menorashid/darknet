import os
import sys
from helpers import util, visualize
import numpy as np
import scipy.misc
# import cv2
import glob
import argparse
import subprocess
import datetime
import time
import matplotlib.pyplot as plt
import get_video_results as gvr

def convert_boxes(boxes, old_size, new_size, expand_percent = 0.1):
	assert 0.<expand_percent<1.
	to_div = np.array([old_size[0],old_size[0],old_size[1],old_size[1]])[np.newaxis,:]
	to_mul = np.array([new_size[0],new_size[0],new_size[1],new_size[1]])[np.newaxis,:]
	
	boxes_new = boxes/to_div * to_mul
	width_expand = expand_percent*(boxes[:,1]-boxes[:,0])[np.newaxis,:]
	height_expand = expand_percent*(boxes[:,3]-boxes[:,2])[np.newaxis,:]
	expander = np.concatenate([-1*width_expand,width_expand,-1*height_expand,height_expand],axis = 1)

	clip_vals = np.array([0,new_size[0],0,new_size[1]])[np.newaxis,:]

	# print expander.shape
	boxes_new = boxes_new + expander

	boxes_new = boxes_new.astype(int)
	# print boxes_new

	boxes_new[:,:2] = np.clip(boxes_new[:,:2],0,new_size[0])
	boxes_new[:,2:] = np.clip(boxes_new[:,2:],0,new_size[1])

	# boxes_new[:,2] = np.max(boxes_new[:,2],0)
	# print new_size[0]
	# boxes_new[:,1] = np.min(boxes_new[:,1],new_size[0])
	# boxes_new[:,3] = np.min(boxes_new[:,3],new_size[1])
	# print boxes_new
	return boxes_new


def get_rel_info(boxes_all,times):
	times_keep = []
	idx_times_keep = []
	boxes_keep = []
	boxes_class_keep = []

	for idx_time_curr, time_curr in enumerate(times):
		for box_class,box in enumerate(boxes_all[:,idx_time_curr,:]):
			if box[0]>-1:
				boxes_keep.append(box[np.newaxis,:])
				boxes_class_keep.append(box_class)
				times_keep.append(time_curr)
				idx_times_keep.append(idx_time_curr)

	boxes_keep = np.concatenate(boxes_keep,axis = 0)
	boxes_class_keep = np.array(boxes_class_keep)
	times_keep = np.array(times_keep)
	idx_times_keep = np.array(idx_times_keep)

	print 'boxes_keep.shape',boxes_keep.shape
	print 'boxes_class_keep.shape',boxes_class_keep.shape
	print 'times_keep.shape',times_keep.shape
	print 'idx_times_keep.shape',idx_times_keep.shape

	return boxes_keep, boxes_class_keep, times_keep, idx_times_keep

def save_bbox(vid_file, out_dir, old_size, time_curr, idx_time_curr, box, box_class):



	command = util.get_extract_image_command(vid_file, out_dir, time_curr, idx_time_curr+1, size_output = None)
	out_file = command.split(' ')
	out_file = out_file[-2].strip('"')
	if not os.path.exists(out_file):
		subprocess.call(command,shell = True)

	im = scipy.misc.imread(out_file)
	new_size = [im.shape[1],im.shape[0]]
	
	box = convert_boxes(box[np.newaxis,:], old_size, new_size, expand_percent = 0.1)[0]
	
	file_name = os.path.split(out_file)[1]
	file_name = file_name[:file_name.rindex('.')]
	out_file_box = os.path.join(out_dir,file_name+'_'+str(box_class)+'.jpg')

	im_box = im[box[2]:box[3],box[0]:box[1],:]
	scipy.misc.imsave(out_file_box, im_box)
	return out_file_box

def write_test_file(out_file_boxes, dummy_kp_file, out_file_test):
	lines = []
	dummy_kp_file =  os.path.abspath(dummy_kp_file)
	for file_curr in out_file_boxes:
		file_curr = os.path.abspath(file_curr)
		line_curr = ' '.join([file_curr,dummy_kp_file])
		lines.append(line_curr)
	util.writeFile(out_file_test, lines)
	return os.path.abspath(out_file_test),len(lines)


def main():
	vid_file = '../data/Cisi_kortsida.MP4'
	res_dir = '../data/Cisi_kortsida_result_files_dummy'
	out_dir = '../data/Cisi_kortsida_kp_frames'

	vid_file = '../data/Oregano_langsida.MP4'
	res_dir = '../data/Oregano_langsida_result_files'
	out_dir = '../data/Oregano_langsida_kp_frames'

	vid_name = 'Soft_left_walk_DG.MP4'
	vid_name = 'ch06_20180501180738.mp4'
	vid_file = os.path.join('../data',vid_name)
	vid_name = vid_name[:vid_name.rindex('.')]
	res_dir = os.path.join('../data',vid_name+'_result_files')
	out_dir = os.path.join('../data',vid_name+'_kp_frames')
	# idx_time_curr = 50
	
	util.mkdir(out_dir)
	old_size = [416,416]

	res_file = os.path.join(res_dir,'results_collated.npz')
	results = np.load(res_file)
	boxes_all = results['boxes']
	times = results['times']
	det_confs = results['det_confs']
	print results.keys()


	boxes_keep, boxes_class_keep, times_keep, idx_times_keep = get_rel_info(boxes_all, times)
	
	out_file_boxes = []
	for idx_box in range(len(boxes_keep)):

		idx_time_curr = idx_times_keep[idx_box]
		time_curr = times_keep[idx_box]
		box = boxes_keep[idx_box]
		# [np.newaxis,:]
		box_class = boxes_class_keep[idx_box]
		out_file_box = save_bbox(vid_file, out_dir, old_size, time_curr, idx_time_curr, box, box_class)
		out_file_boxes.append(out_file_box)

	dummy_kp_file = '../data/dummy_kp.npy'
	out_file_test = os.path.join(out_dir,'test_kp.txt')
	out_file_test, num_lines = write_test_file(out_file_boxes,dummy_kp_file, out_file_test)
	
	path_to_th = '../animal_human_kp/torch'
	path_back = '../../darknet'

	out_dir_kp = os.path.abspath(os.path.join(out_dir,'kp'))

	command = []
	command.extend(['cd',path_to_th,'&&'])
	command.extend(['th','test.th'])
	command.extend(['-val_data_path',out_file_test])
	command.extend(['-out_dir_images',out_dir_kp])
	command.extend(['-batchSize',str(num_lines)])
	command.extend(['-iterations',str(1)])
	command.extend(['&&','cd',path_back])
	command = ' '.join(command)
	print command





	# print command


if __name__=='__main__':
	main()