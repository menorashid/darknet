# import matplotlib
import numpy as np;
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import sys
sys.path.append('..')
from helpers import util
# , visualize
import numpy as np
import scipy.misc
# import cv2
import glob
# from skimage.draw import rectangle
import random
import shutil

def get_annos_numpy(line_curr):
	annos = line_curr.split(' ')

	annos = annos[1:]
	annos = [int(float(val)) for val in annos]
	bbox = np.array(annos[:4])
	annos = np.array(annos[4:])
	annos = np.reshape(annos,(5,3))
	return bbox,annos

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


def get_anno_str_format(im,bbox,object_cat):
	# im = cv2.imread(im_file)
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
	return str_format
	

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

def make_kp_front_side_lists():
	anno_dir = '../../data/horse_data_cleaned'
	out_dir = '../../data/horse_data_cleaned_yolo'
	anno_files = [os.path.join(anno_dir,file_curr) for file_curr in ['trainImageList.txt','valImageList.txt']]
	
	for anno_file in anno_files:
		out_file = os.path.split(anno_file)[1][:-13]
		out_file = os.path.join(out_dir,out_file+'_kp_front_side.txt')

		print out_file
		dict_name_sort = {}
		dict_name_sort['front'] = [] # all points visible
		dict_name_sort['side'] = [] # 3 points visible
		dict_name_sort['four_points'] = [] # 4 points or 
		dict_name_sort['other'] = [] #the wrong 3 visible

	
		for line_curr in util.readLinesFromFile(anno_file):
			im_file_out = line_curr.split(' ')[0][2:].replace('/','_')
			im_file_out = im_file_out[:im_file_out.rindex('.')]+'.jpg'
			bbox, annos = get_annos_numpy(line_curr)
			if np.sum(annos[:,2]>0)==5:
				dict_name_sort['front'].append(im_file_out)
			elif np.sum(annos[:,2]>0)==4:
				dict_name_sort['four_points'].append(im_file_out)
			elif np.sum(annos[:,2]>0)==3:
				if np.all(annos[:,2]==np.array([-1,1,1,-1,1])) or np.all(annos[:,2]==np.array([1,-1,1,1,-1])):
					dict_name_sort['side'].append(im_file_out)
				else:
					dict_name_sort['other'].append(im_file_out)
			else:
				dict_name_sort['other'].append(im_file_out)

		list_files = []
		for idx_key,key in enumerate(dict_name_sort.keys()):
			list_files.extend([file_curr+' '+str(idx_key) for file_curr in dict_name_sort[key]])

			print key,len(dict_name_sort[key])
		util.writeFile(out_file,list_files)
		print out_file,len(list_files)

def visualize_front_side_lists():
	dir_server = '/disk3'
	out_dir = os.path.join(dir_server,'maheen_data','eccv_18','data/horse_data_cleaned_yolo')
	data_dirs = ['train','test']
	list_files = ['train_kp_front_side.txt','val_kp_front_side.txt']
	for data_dir,list_file in zip(data_dirs,list_files):
		out_file_html = os.path.join(out_dir,list_file[:list_file.rindex('.')]+'.html')
		im_list = util.readLinesFromFile(os.path.join(out_dir,list_file))
		im_list = [line_curr.split(' ') for line_curr in im_list]
		im_list = np.array(im_list)
		nums = np.unique(im_list[:,1])
		ims_html = []
		captions_html = []
		for num_curr in nums:
			ims_curr = im_list[im_list[:,1]==num_curr,0]
			ims_curr = [os.path.join(out_dir,data_dir,im_curr.replace('+','%2B')) for im_curr in ims_curr]
			ims_html.append([util.getRelPath(im_curr,dir_server) for im_curr in ims_curr])
			captions_html.append([num_curr for im_curr in ims_curr])
		ims_html = [list(i) for i in zip(*ims_html)]
		captions_html = [list(i) for i in zip(*captions_html)]
		visualize.writeHTML(out_file_html,ims_html,captions_html,100,100)

def write_side_anno_files(im_list_rel,data_dir,out_data_dir,write_val):
	# print 'len(im_list_rel)', len(im_list_rel)
	for im_curr in im_list_rel:
		in_anno_file = os.path.join(data_dir,im_curr[:im_curr.rindex('.')]+'.txt')
		out_anno_file = os.path.join(out_data_dir,im_curr[:im_curr.rindex('.')]+'.txt')
		in_anno = util.readLinesFromFile(in_anno_file)[0]
		out_anno = [str(write_val)+' '+' '.join(in_anno.split(' ')[1:])]
		
		# print 'in_anno_file', in_anno_file
		# print 'out_anno_file', out_anno_file
		# print 'in_anno', in_anno
		# print 'out_anno', out_anno
		# raw_input()
		# break

		util.writeFile(out_anno_file,out_anno)

def write_front_side_files():
	out_dir = '../../data/horse_data_cleaned_yolo'
	out_dir_write = out_dir.replace('../../','../')

	data_dirs = ['train','test']
	list_files = ['train_kp_front_side.txt','val_kp_front_side.txt']
	out_files = ['train_side.txt','test_side.txt']
	new_data_dirs = ['train_side','test_side']

	map_vals = [[0,1],[2,0]] #front is class 1,side is class 0
	
	for idx in range(len(data_dirs)):
		data_dir = os.path.join(out_dir,data_dirs[idx])
		list_file = os.path.join(out_dir,list_files[idx])
		out_file = os.path.join(out_dir,out_files[idx])
		out_data_dir = os.path.join(out_dir,new_data_dirs[idx])
		out_data_dir_write = out_data_dir.replace(out_dir,out_dir_write)

		im_list = util.readLinesFromFile(list_file)
		im_list = [line_curr.split(' ') for line_curr in im_list]
		im_list = np.array(im_list)
		vp = im_list[:,1].astype(np.int)
		im_list = im_list[:,0]
		
		print 'len(im_list)', len(im_list)
		im_list_to_write = []
		for vp_val,write_val in map_vals:
			im_list_rel = im_list[vp==vp_val]
			write_side_anno_files(im_list_rel,data_dir,out_data_dir,write_val)
			im_list_to_write = im_list_to_write + list(im_list_rel)  

		im_list_to_write = [os.path.join(out_data_dir_write,file_curr) for file_curr in im_list_to_write]
		print 'len(im_list_to_write)', len(im_list_to_write)
		print 'im_list_to_write[0]', im_list_to_write[0]
		print 'out_file', out_file

		util.writeFile(out_file,im_list_to_write)

def scratch():
	# make_kp_front_side_lists()
	# visualize_front_side_lists()
	# write_front_side_files()

	# return
	
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

def get_manual_anno_classes():
	frame_dir = '../../data/frames/ch06_20161212115301_frames'
	# ch02_20161212115300_frames'
	label_dir = os.path.join(frame_dir,'labels')
	out_dir = os.path.join(frame_dir,'labels_with_class')
	util.mkdir(out_dir)

	im_files = glob.glob(os.path.join(frame_dir,'*.jpg'))
	im_files.sort()
	print len(im_files)
	plt.ion()
	for im_num,im_file in enumerate(im_files):
		print im_file,im_num,len(im_files)
		label_file = im_file.replace(frame_dir,label_dir).replace('.jpg','.txt')
		out_file = im_file.replace(frame_dir,out_dir).replace('.jpg','.txt')

		assert os.path.exists(label_file)
		label_info = util.readLinesFromFile(label_file)
		num_boxes = int(label_info[0])
		if num_boxes>0:
			assert num_boxes==1
			box = [int(val) for val in label_info[1].split(' ')]
			im = scipy.misc.imread(im_file)
			# im = cv2.rectangle(im,(box[0],box[1]),(box[2],box[3]),(255,0,0),5)
			plt.figure()
			plt.imshow(im)
			val = raw_input('whats the class')
			label_info.append(val)
			util.writeFile(out_file,label_info)
			plt.close()


def scratch_1():
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

def write_manual_anno_files():
	im_dir = '../../data/frames/ch02_20161212115300_frames'
	# ch06_20161212115301_frames'
	# 
	label_dir = os.path.join(im_dir,'labels')
	class_dir = os.path.join(im_dir,'labels_with_class')
	label_files = glob.glob(os.path.join(class_dir,'*.txt'))
	label_files.sort()

	lines = []
	out_file_info = im_dir+'_class_ims.txt'


	# plt.ion()
	for label_file in label_files:
		anno = util.readLinesFromFile(label_file)
		im_name = os.path.split(label_file)[1].replace('.txt','')
		im_file = os.path.join(im_dir,im_name+'.jpg')
		out_file_anno = os.path.join(im_dir,im_name+'.txt')

		print anno
		object_cat = int(anno[2])
		
		if object_cat>1:
			continue

		bbox = np.array([int(val) for val in anno[1].split(' ')]) #xmin ymin xmax ymax
		# coords = [[bbox[0],bbox[0],bbox[2],bbox[2],bbox[0]],[bbox[1],bbox[3],bbox[3],bbox[1],bbox[1]]]
		
		im = scipy.misc.imread(im_file)
		bbox = bbox[[0,2,1,3]] # xmin xmax ymin ymax

		str_format = get_anno_str_format(im,bbox,object_cat)
		util.writeFile(out_file_anno,[str_format])

		lines.append(im_file +' '+str(object_cat))
		# coords = [[bbox[0],bbox[0],bbox[1],bbox[1],bbox[0]],[bbox[2],bbox[3],bbox[3],bbox[2],bbox[2]]]

		# coords = np.array(coords).T
		
		# plt.figure()
		# plt.imshow(im)
		# plt.plot(coords[:,0],coords[:,1],'-b')

		# # # coords = rectangle((bbox[1],bbox[0]),end = (bbox[1],bbox[0]),shape = im.shape)
		# # print coords
		# raw_input()
	util.writeFile(out_file_info, lines)

def write_manual_neg_anno_files():
	im_dir = '../../data/frames/ch06_20161212115301_frames'
	# ch02_20161212115300_frames'
	# 
	class_info_file = im_dir+'_class_ims.txt'
	im_files = util.readLinesFromFile(class_info_file)
	im_files = [file_curr.split(' ')[0] for file_curr in im_files]
	im_files_all = glob.glob(os.path.join(im_dir,'*.jpg'))
	print im_files_all[0]
	left_overs = [file_curr for file_curr in im_files_all if file_curr not in im_files]
	print len(left_overs),len(im_files), len(im_files_all)
	for file_curr in left_overs:
		out_file = file_curr.replace('.jpg','.txt')
		# print out_file
		# assert not os.path.exists(out_file)
		util.writeFile(out_file,[''])

	
def make_test_files_manual_anno():
	data_dir = '../../data/frames'
	
	files = [os.path.join(data_dir,file_name) for file_name in ['ch06_20161212115301_frames_class_ims.txt','ch02_20161212115300_frames_class_ims.txt']]
	
	all_files = util.readLinesFromFile(files[0])+util.readLinesFromFile(files[1])
	print len(all_files)
	random.shuffle(all_files)
	train_files = all_files[:-20]
	test_files = all_files[-20:]
	print len(train_files),len(test_files),len(train_files)+len(test_files)
	# return
	out_dir = os.path.join(data_dir,'test_frames')
	util.mkdir(out_dir)
	files = []
	out_file_list = os.path.join(data_dir,'test_frames.txt')
	for file_curr in test_files:
		file_curr = file_curr.split(' ')[0]
		out_file = os.path.join(out_dir,os.path.split(file_curr)[1])
		shutil.move(file_curr,out_file)
		file_curr = file_curr.replace('.jpg','.txt')
		out_file = out_file.replace('.jpg','.txt')
		shutil.move(file_curr,out_file)
		files.append(out_file)
	util.writeFile(out_file_list,files)
	
	# test_frames = util.readLinesFromFile(out_file_list)
	# for test_frame in test_frames:
	# 	file_name = os.path.split(test_frame)[1]
	# 	in_file_dir = os.path.join(data_dir,file_name[:file_name.rindex('_')]+'_frames')
	# 	print in_file_dir
	# 	in_file = os.path.join(in_file_dir,file_name.replace('.jpg','.txt'))
	# 	out_file = os.path.join(out_dir,os.path.split(in_file)[1])
	# 	print in_file,out_file
	# 	print os.path.exists(in_file)
	# 	print os.path.exists(out_file)
	# 	shutil.move(in_file,out_file)



def main():
	out_dir = '../../data/horse_data_cleaned_yolo'

	to_comb = [os.path.join(out_dir,'train_side.txt'),os.path.join(out_dir,'train_add_manual.txt')]
	out_file = os.path.join(out_dir,'train_side_wframes.txt')

	# to_comb = [os.path.join(out_dir,'test_side.txt'),os.path.join(out_dir,'test_add_manual.txt')]
	# out_file = os.path.join(out_dir,'test_side_wframes.txt')

	lines_all = []
	for idx_file_curr,file_curr in enumerate(to_comb):
		lines = util.readLinesFromFile(file_curr)
		if idx_file_curr == 1:
			lines = [line.replace('.txt','.jpg') for line in lines]
		print len(lines)
		lines_all = lines_all+lines
	print len(lines_all)
	print len(list(set(lines_all)))

	util.writeFile(out_file,lines_all)


	return
	out_dir = '../../data/frames'
	out_dir_write_train = '../data/horse_data_cleaned_yolo/train_side'
	out_dir_write_test = '../data/horse_data_cleaned_yolo/test_side'
	
	out_file_train_add = os.path.join(out_dir,'train_add_manual.txt')
	out_file_test_add = os.path.join(out_dir,'test_add_manual.txt')

	frame_dirs = ['ch02_20161212115300_frames','ch06_20161212115301_frames']
	
	train_files = []
	for frame_dir in frame_dirs:
		print os.path.join(out_dir,frame_dir,'*.jpg')
		train_files.extend(glob.glob(os.path.join(out_dir,frame_dir,'*.jpg')))
	print len(train_files)
	print train_files[0]

	train_files_write = []
	for train_file in train_files:
		train_file = os.path.split(train_file)[1]
		train_file = os.path.join(out_dir_write_train,train_file)
		print train_file
		train_files_write.append(train_file)
	util.writeFile(out_file_train_add,train_files_write)

	test_files = util.readLinesFromFile(os.path.join(out_dir,'test_frames.txt'))
	print len(test_files)
	print test_files[0]
	test_files_write = []
	for test_file in test_files:
		test_file = os.path.split(test_file)[1]
		test_file = os.path.join(out_dir_write_test,test_file)
		test_files_write.append(test_file)
		print test_file
	util.writeFile(out_file_test_add,test_files_write)



		

	# write_manual_neg_anno_files()

	# make empty files for the rest





	

	

if __name__=='__main__':
	main()


