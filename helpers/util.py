import numpy as np;
import scipy
import subprocess;
import os;


def getFilesInFolder(folder,ext):
    list_files=[os.path.join(folder,file_curr) for file_curr in os.listdir(folder) if file_curr.endswith(ext)];
    return list_files;     
    
def getStartingFiles(dir_curr,img_name):
    files=[file_curr for file_curr in os.listdir(dir_curr) if file_curr.startswith(img_name)];
    return files;

def getEndingFiles(dir_curr,img_name):
    files=[file_curr for file_curr in os.listdir(dir_curr) if file_curr.endswith(img_name)];
    return files;


def getFileNames(file_paths,ext=True):
    just_files=[file_curr[file_curr.rindex('/')+1:] for file_curr in file_paths];
    file_names=[];
    if ext:
        file_names=just_files;
    else:
        file_names=[file_curr[:file_curr.rindex('.')] for file_curr in just_files];
    return file_names;

def getRelPath(file_curr,replace_str='/disk2'):
    count=file_curr.count('/');
    str_replace='../'*count
    rel_str=file_curr.replace(replace_str,str_replace);
    return rel_str;

def mkdir(dir_curr):
    if not os.path.exists(dir_curr):
        os.mkdir(dir_curr);

def makedirs(dir_curr):
    if not os.path.exists(dir_curr):
        os.makedirs(dir_curr);


def getIndexingArray(big_array,small_array):
    small_array=np.array(small_array);
    big_array=np.array(big_array);
    assert np.all(np.in1d(small_array,big_array))

    big_sort_idx= np.argsort(big_array)
    small_sort_idx= np.searchsorted(big_array[big_sort_idx],small_array)
    index_arr = big_sort_idx[small_sort_idx]
    return index_arr

def getIdxRange(num_files,batch_size):
    idx_range=range(0,num_files+1,batch_size);
    if idx_range[-1]!=num_files:
        idx_range.append(num_files);
    return idx_range;

def readLinesFromFile(file_name):
    with open(file_name,'rb') as f:
        lines=f.readlines();
    lines=[line.strip('\n') for line in lines];
    return lines

def normalize(matrix,gpuFlag=False):
    if gpuFlag==True:
        import cudarray as ca
        norm=ca.sqrt(ca.sum(ca.power(matrix,2),1,keepdims=True));
        matrix_n=matrix/norm
    else:
        norm=np.sqrt(np.sum(np.square(matrix),1,keepdims=True));
        matrix_n=matrix/norm
    
    return matrix_n

def getHammingDistance(indices,indices_hash):
    ham_dist_all=np.zeros((indices_hash.shape[0],));
    for row in range(indices_hash.shape[0]):
        ham_dist_all[row]=scipy.spatial.distance.hamming(indices[row],indices_hash[row])
    return ham_dist_all    

def product(arr):
    p=1;
    for l in arr:
        p *= l
    return p;

def get_all_plotting_vals(det_confs, times, boxes,fps):
    det_confs_plot = [[],[]]
    # if smooth:
    for idx, det in enumerate(det_confs):
        smooth_window = min(int(round(60/float(fps))),len(det))
        box = np.ones((smooth_window,))/float(smooth_window)
        det_confs_plot[idx] = np.convolve(np.array(det), box, mode='same') 
    vals = [(times, val) for val in det_confs]
    smoothvals = [(times, val) for val in det_confs_plot]

    legend_entries = ['Side','Front','Side Raw','Front Raw']
    
    xAndYs = smoothvals+vals
    # xAndYs_smooth = smoothvals
    colors = ['C0','C1','C0','C1']
    alphas = [1.,1.,0.3,0.3]
    markers = ['o']*4
    markersize = [2]*4
    colors_etc = [colors, alphas, markers, markersize]
    # colors_etc_smooth = [val[:2] for val in colors_etc]

    xlabel = 'Video Time (min)'
    ylabel = 'Detection Confidence'
    title = 'Face Detections Over Time'
    labels = [xlabel, ylabel]
    return xAndYs, colors_etc, labels, title, legend_entries

def get_extract_image_command(vid_file, out_dir, time_curr, idx_time_curr, size_output = [416,416]):
    video_name = os.path.split(vid_file)[1]
    video_name = video_name[:video_name.rindex('.')]

    out_file_curr = video_name+'_'+format(idx_time_curr, '09d')+'.jpg'
    out_file_format = os.path.join(out_dir, out_file_curr)
    # print out_file_format

    # sec_format = str(datetime.timedelta(seconds=time_curr))
    # m, s = divmod(time_curr, 60.)
    # h, m = divmod(m, 60.)
    # str_secs = '%d:%02d:%05f' % (h, m, s)
    str_secs = convert_sec_to_str(time_curr, 5)
    command = []
    command.extend(['ffmpeg'])
    command.extend(['-ss',str_secs])
    command.extend(['-y'])
    command.extend(['-i','"'+vid_file+'"'])
    command.extend(['-vframes',str(1)])
    if size_output is not None:
        command.extend(['-s',str(size_output[0])+'x'+str(size_output[1])])
    command.append('"'+out_file_format+'"')
    command.append('-hide_banner')
    command = ' '.join(command)
    return command
    # subprocess.call(command, shell=True)

def getIOU(box_1,box_2):
    box_1=np.array(box_1);
    box_2=np.array(box_2);
    minx_t=min(box_1[0],box_2[0]);
    miny_t=min(box_1[1],box_2[1]);
    min_vals=np.array([minx_t,miny_t,minx_t,miny_t]);
    box_1=box_1-min_vals;
    box_2=box_2-min_vals;
    # print box_1,box_2
    maxx_t=max(box_1[2],box_2[2]);
    maxy_t=max(box_1[3],box_2[3]);
    img=np.zeros(shape=(maxx_t,maxy_t));
    img[box_1[0]:box_1[2],box_1[1]:box_1[3]]=1;
    img[box_2[0]:box_2[2],box_2[1]:box_2[3]]=img[box_2[0]:box_2[2],box_2[1]:box_2[3]]+1;
    # print np.min(img),np.max(img)
    count_union=np.sum(img>0);
    count_int=np.sum(img==2);
    # print count_union,count_int
    # plt.figure();
    # plt.imshow(img,vmin=0,vmax=10);
    # plt.show();
    iou=count_int/float(count_union);
    return iou

def escapeString(string):
    special_chars='!"&\'()*,:;<=>?@[]`{|}';
    for special_char in special_chars:
        string=string.replace(special_char,'\\'+special_char);
    return string

def replaceSpecialChar(string,replace_with):
    special_chars='!"&\'()*,:;<=>?@[]`{|}';
    for special_char in special_chars:
        string=string.replace(special_char,replace_with);
    return string

def writeFile(file_name,list_to_write, uni_it = False):
    if uni_it:
        file_name = unicode(file_name, "utf-8")
    #     print type(file_name)
    # print file_name

    with open(file_name,'wb') as f:
        for string in list_to_write:
            f.write(string+'\n');

def getAllSubDirectories(meta_dir):
    # meta_dir=escapeString(meta_dir);
    command='find '+meta_dir+' -type d';
    print command
    sub_dirs=subprocess.check_output(command,shell=True)
    sub_dirs=sub_dirs.split('\n');
    sub_dirs=[dir_curr for dir_curr in sub_dirs if dir_curr];
    return sub_dirs
    
def convert_sec_to_str(time_curr,num_decimal = 3):
    m, s = divmod(time_curr, 60.)
    h, m = divmod(m, 60.)
    str_secs = '%d:%02d:%.'+str(num_decimal)+'f'
    str_secs = str_secs % (h, m, s)
    return str_secs
