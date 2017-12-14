import os
import sys
sys.path.append('..')
from helpers import util, visualize
import numpy as np
import scipy.misc
import cv2
import glob

def just_visualize():
	dir_server = '/disk3'
	horse_dir = os.path.join(dir_server,'maheen_data','eccv_18','data/horse_data_cleaned')

	train_file = os.path.join(horse_dir,'trainImageList.txt')
	train_file = os.path.join(horse_dir,'valImageList.txt')
	out_file_html = train_file[:train_file.rindex('.')]+'.html'

	train_data = util.readLinesFromFile(train_file)
	im_files = []
	for line in train_data:
		im_file = line.split(' ')[0]
		im_file = im_file[2:]
		print im_file
		im_file = os.path.join(horse_dir,im_file)
		im_file = util.getRelPath(im_file,dir_server)
		im_files.append(im_file)

	idx_splits = list(np.linspace(0, len(train_data), num=100, endpoint=True).astype(int))
	print idx_splits

	im_html = []
	captions_html = []
	for idx_idx, start_idx in enumerate(idx_splits[:-1]):
		end_idx = idx_splits[idx_idx+1]
		row_curr = im_files[start_idx:end_idx]
		im_html.append(row_curr)
		captions_html.append(['']*len(row_curr))
		

	visualize.writeHTML(out_file_html,im_html,captions_html,100,100)
	print out_file_html.replace(dir_server,'http://vision3.cs.ucdavis.edu:1000/')

def save_im_anno(train_file,out_dir):
	
	train_data = util.readLinesFromFile(train_file)
	im_files = []
	object_cat = 0
	
	for idx_line, line in enumerate(train_data):
		print idx_line
		anno = line.split(' ')

		im_file = anno[0][2:]
		out_file = im_file[:im_file.rindex('.')]
		out_file = os.path.join(out_dir,out_file.replace('/','_'))
		
		if os.path.exists(out_file+'.jpg'):
			continue
		
		anno = anno[1:]
		im_file = os.path.join(horse_dir,im_file)

		im = cv2.imread(im_file)
		# print line
		# print anno
		anno = [float(val) for val in anno]
		kp = anno[-15:]
		bbox = anno[:-15]
		# print bbox

		w = im.shape[1]
		h = im.shape[0]
		width = bbox[1]-bbox[0]
		height = bbox[3]-bbox[2]
		x = bbox[0]+(width/2.)
		y = bbox[2]+(height/2.)
		x = x/float(w)
		y = y/float(h)
		width = width/float(w)
		height = height/float(h)

		str_format = '%d %.6f %.6f %.6f %.6f' %(object_cat, x, y, width, height)
		
		out_file_im = out_file+'.jpg'
		cv2.imwrite(out_file_im,im)		
		out_file_anno = out_file+'.txt' 
		util.writeFile(out_file_anno,[str_format])
		im_files.append(out_file_im)
		

	print len(im_files)
	print im_files[0]
	print len(list(set(im_files)))

def main():
	dir_server = '/disk3'
	horse_dir = os.path.join(dir_server,'maheen_data','eccv_18','experiments','yolo_all_horse_face_correct_output/results')

	im_files_org = glob.glob(os.path.join(horse_dir,'*.jpg'))

	# train_file = os.path.join(horse_dir,'trainImageList.txt')
	# train_file = os.path.join(horse_dir,'valImageList.txt')
	out_file_html = os.path.join(horse_dir,'det.html')
	# train_file[:train_file.rindex('.')]+'.html'

	# train_data = util.readLinesFromFile(train_file)
	im_files = []
	for im_file in im_files_org:
		# im_file = line.split(' ')[0]
		# im_file = im_file[2:]
		# print im_file
		# im_file = os.path.join(horse_dir,im_file)
		print im_file
		im_file = util.getRelPath(im_file,dir_server)
		print im_file
		im_files.append(im_file)

	idx_splits = list(np.linspace(0, len(im_files), num=50, endpoint=True).astype(int))
	print idx_splits

	im_html = []
	captions_html = []
	for idx_idx, start_idx in enumerate(idx_splits[:-1]):
		end_idx = idx_splits[idx_idx+1]
		row_curr = im_files[start_idx:end_idx]
		im_html.append(row_curr)
		captions_html.append(['']*len(row_curr))
		

	visualize.writeHTML(out_file_html,im_html,captions_html,224,224)
	print out_file_html.replace(dir_server,'http://vision3.cs.ucdavis.edu:1000/')

	return
	dir_server = '/disk3'
	horse_dir = os.path.join(dir_server,'maheen_data','eccv_18','data/horse_data_cleaned')

	train_file = os.path.join(horse_dir,'trainImageList.txt')
	test_file = os.path.join(horse_dir,'valImageList.txt')
	
	
	out_dirs = ['../../data/horse_data_cleaned_yolo/train','../../data/horse_data_cleaned_yolo/test']
	
	# for file_curr, out_dir in zip([train_file,test_file],out_dirs):
	# 	util.makedirs(out_dir)
	# 	save_im_anno(file_curr,out_dir)
	to_replace = ['../../','../']
	for out_dir in out_dirs:
		out_file = out_dir+'_all_face.txt'
		ims = glob.glob(os.path.join(out_dir,'*.jpg'))
		print len(ims),ims[0]
		ims = [im_curr.replace(to_replace[0],to_replace[1]) for im_curr in ims]
		print ims[0]
		print out_file
		util.writeFile(out_file,ims)



	

	

if __name__=='__main__':
	main()


