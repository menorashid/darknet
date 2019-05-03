import matplotlib
import numpy as np;
# matplotlib.use('TkAgg')
matplotlib.use('TkAgg',warn=False, force=True)
from matplotlib import pyplot as plt
print "Using:",matplotlib.get_backend()

# import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
import os;
import sys
import datetime
from helpers import util
import subprocess
import scipy.misc
import matplotlib.patches as patches
import time


class Gui:
    def __init__(self, res_file, vid_name, fps, size_output, frame_dir):
    # (self, vals, smoothvals, vid_name, boxes, fps, size_output):

        # self.vals_handles = []
        loaded = np.load(res_file)
        det_confs = loaded['det_confs']
        times = loaded['times']
        boxes = loaded['boxes']

        xAndYs, colors_etc, _, _, legend_entries = util.get_all_plotting_vals(det_confs, times, boxes,fps)
        self.xAndYs = xAndYs
        self.colors_etc = colors_etc
        self.labels = legend_entries
        self.frame_dir = frame_dir

        self.handles = []
        plt.ion()
        print 'ion'
        self.fig = plt.figure(num = 'Detection Plot')
        self.im_fig = None
        # self.im = np.random.random((240,240,3))
        self.size_output = size_output
        self.vid_name = vid_name
        self.out_dir_scratch = './scratch'
        self.boxes = boxes
        util.mkdir(self.out_dir_scratch)
        
        self.fps = fps
        
        # self.labels_smooth = ['Side','Front']
        # self.labels = ['Side','Front','Side Raw','Front Raw']
        
        # self.xAndYs = smoothvals+vals
        # # self.xAndYs_smooth = smoothvals
        # # colors = ['C0','C1','C0','C1']
        # # alphas = [1.,1.,0.3,0.3]
        # # markers = ['o']*4
        # # markersize = [2]*4
        # self.colors_etc = [colors, alphas, markers, markersize]
        # # self.colors_etc_smooth = [val[:2] for val in self.colors_etc]

        self.plot(self.xAndYs, self.labels, self.colors_etc)
        
        self.in_click = False
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('close_event', self.on_exit)
        
    def on_exit(self,event):
        sys.exit(0)
        
    def plot(self, xAndYs, legend_entries, colors_etc ,suptitle = 'Click on plot to start'):
        
        plt.figure(self.fig.number)
        plt.clf()
        xlabel = 'Video Time (min)'
        ylabel = 'Detection Confidence'
        title = 'Face Detections Over Time'
        plt.suptitle(suptitle)
        plt.title(title);
        plt.grid(1);
        plt.xlabel(xlabel);
        plt.ylabel(ylabel);
        self.handles = []
        for idx_x_y,(x,y) in enumerate(xAndYs):
            x_min = x/60.
            handle,=plt.plot(x_min,y,color = colors_etc[0][idx_x_y], alpha = colors_etc[1][idx_x_y], marker = colors_etc[2][idx_x_y], markersize = colors_etc[3][idx_x_y], picker = self.fps)
            self.handles.append(handle);

        if legend_entries is not None:
            lgd=plt.legend(self.handles,legend_entries,loc=0)    
        plt.show() 


    def process_coord(self,coord):
        coord_x,coord_y = coord[0]
        coord_x_sec = coord_x*60.
        # print coord_x, coord_y

        x_vals = self.xAndYs[0][0]
        diffs = np.abs(x_vals - coord_x_sec)
        idx_min = np.argmin(diffs)
        # print idx_min, diffs[idx_min], x_vals[idx_min]

        time_curr = x_vals[idx_min]

        plt.figure(self.fig.number)
        ylim_bef = plt.gca().get_ylim()
        xlim_bef = plt.gca().get_xlim()

        y_max = np.max([np.max(x_y_curr[1]) for x_y_curr in self.xAndYs])
        plt.xlim(xlim_bef)
        plt.ylim(ylim_bef)
        # print y_lim
        plt.plot([time_curr/60.,time_curr/60.],[0,y_max],'-r') 

        str_secs = util.convert_sec_to_str(time_curr,num_decimal = 3)
        # m, s = divmod(time_curr, 60.)
        # h, m = divmod(m, 60.)
        # str_secs = '%d:%02d:%.3f' % (h, m, s)

        return idx_min, time_curr, str_secs

        # num_coords = np.max(self.xAndYs[2][0])
        # print num_coords

        # coord_x = int(np.clip(int(coord_x),0,num_coords))
        # print coord_x


    def extract_image(self, time_curr, idx_time_curr):

        video_name = os.path.split(self.vid_name)[1]
        video_name = video_name[:video_name.rindex('.')]


        out_file_curr = video_name+'_'+format(idx_time_curr+1, '09d')+'.jpg'
        out_file_format = os.path.join(self.frame_dir, out_file_curr)
        if os.path.exists(out_file_format):
            return out_file_format
        else:
            command = util.get_extract_image_command(self.vid_name, self.frame_dir, time_curr, idx_time_curr+1, self.size_output)
            subprocess.call(command, shell=True)

        return out_file_format

    def plot_im(self, out_file_im, idx_time, str_time_curr):

        if self.im_fig is None:
            self.im_fig = plt.figure(num = 'Image Plot')
        else:
            plt.figure(self.im_fig.number)
            plt.clf()

        im = scipy.misc.imread(out_file_im)
        plt.imshow(im)
        plt.axis('off')
        strs_title = ['Side Conf','Front Conf']

        str_title = []

        # time_curr = self.xAndYs[0][0][idx_time]
        # m, s = divmod(time_curr, 60.)
        # h, m = divmod(m, 60.)
        # str_secs = '%d:%02d:%.3f' % (h, m, s)
        str_curr = 'Time '+str_time_curr
        str_title.append(str_curr)
        for type_idx in range(self.boxes.shape[0]):
            box = self.boxes[type_idx,idx_time]
            # print self.boxes[:,idx_time,:]
            # print box

            det_conf = self.xAndYs[type_idx+2][1][idx_time]
            # print 'AAAAAAAAAAAAA',type_idx, det_conf 
            str_curr = strs_title[type_idx]+' %.2f' % det_conf
            str_title.append(str_curr)

            if box[0]==-1:
                # str_curr = strs_title[type_idx]+' %.2f' % 0.
                # str_title.append(str_curr)
                continue


            
            width = box[1]-box[0]
            height = box[3]-box[2]
            # print self.colors_etc[0]
            # print type_idx
            
            color_curr = self.colors_etc[0][type_idx]
            # print self.colors_etc[0]
            # print color_curr
            rect = patches.Rectangle((box[0],box[2]),width = width,height = height, edgecolor = color_curr, fill = False, linewidth = 3)
                # ,linewidth=1,edgecolor=self.colors_etc[0][type_idx],facecolor='none')
            plt.gca().add_patch(rect)
        # print str_title
        str_title = ', '.join(str_title)
        plt.title(str_title)


    def on_click(self, event):
        # print 'IN click'
        if self.in_click:
            return

        suptitle_select = 'Select any time point'
        self.plot(self.xAndYs, self.labels, self.colors_etc,suptitle = suptitle_select)
        self.in_click = True
        cursor = Cursor(plt.gca(), useblit=True, color='k', linewidth=1)
        coord = plt.ginput(1)
        idx_time, time_curr, str_time_curr = self.process_coord(coord)
        out_file_im = self.extract_image( time_curr, idx_time)
        print out_file_im
        self.plot_im(out_file_im, idx_time, str_time_curr)
        plt.figure(self.fig.number)
        plt.suptitle('Updated image for '+str_time_curr+' in image window. '+suptitle_select)
        plt.figure(self.im_fig.number)
        # self.im_fig.canvas.manager.window.raise_()
        self.in_click = False








# def onpick(event):

#     if event.artist not in handles: return True
#     # !=line: return True

#     N = len(event.ind)
#     if not N: return True


#     figi = plt.figure()
#     for subplotnum, dataind in enumerate(event.ind):
#         print dataind

#         # ax = figi.add_subplot(N,1,subplotnum+1)
#         # ax.plot(X[dataind])
#         # ax.text(0.05, 0.9, 'mu=%1.3f\nsigma=%1.3f'%(xs[dataind], ys[dataind]),
#         #         transform=ax.transAxes, va='top')
#         # ax.set_ylim(-0.5, 1.5)
#     figi.show()
#     return True

# # fig.canvas.mpl_connect('pick_event', onpick)

# # plt.show()



# def dummy():
#     plt.ion()
#     fig=plt.figure(1)
#     fig.add_subplot(221)

#     # equivalent but more general
#     ax1=fig.add_subplot(2, 2, 1)
#     raw_input()

#     # add a subplot with no frame
#     ax2=fig.add_subplot(222, frameon=False)
#     raw_input()

#     # add a polar subplot
#     fig.add_subplot(223, projection='polar')
#     raw_input()

#     # add a red subplot that share the x-axis with ax1
#     fig.add_subplot(224, sharex=ax1, facecolor='red')
#     raw_input()

#     #delete x2 from the figure
#     fig.delaxes(ax2)
#     raw_input()

#     #add x2 to the figure again
#     fig.add_subplot(ax2)
#     raw_input()



# handles = []

# def plotSimple(xAndYs,out_file=None,title='',xlabel='',ylabel='',legend_entries=None,loc=0,outside=False,logscale=False,colors=None,xticks=None, colors_etc = None, fps = 5):
#     if out_file is None:
#         plt.ion()
#     fig = plt.figure()
#     plt.title(title);
#     plt.grid(1);
#     plt.xlabel(xlabel);
#     plt.ylabel(ylabel);
#     if logscale:
#         plt.gca().set_xscale('log')
#     # assert len(xs)==len(ys)
#     # handles=[];
#     for idx_x_y,(x,y) in enumerate(xAndYs):
#         if colors is not None:
#             color_curr=colors[idx_x_y];
#             handle,=plt.plot(x,y,color_curr)
#                 # ,linewidth=2.0);
#         elif colors_etc is not None:
#             handle,=plt.plot(x,y,color = colors_etc[0][idx_x_y], alpha = colors_etc[1][idx_x_y], marker = colors_etc[2][idx_x_y], markersize = colors_etc[3][idx_x_y], picker = fps)
#         else:
#             handle,=plt.plot(x,y)
#                 # ,linewidth=2.0);

#         handles.append(handle);
#     if legend_entries is not None:
#         if outside:
#             lgd=plt.legend(handles,legend_entries,loc=loc,bbox_to_anchor=(1.05, 1),borderaxespad=0.)
#         else:
#             lgd=plt.legend(handles,legend_entries,loc=loc)    

#     if xticks is not None:
#         ax = plt.gca()
#         ax.set_xticks(xticks)


#     fig.canvas.mpl_connect('pick_event', onpick)

#     if out_file is not None:
#         if legend_entries is not None:
#             plt.savefig(out_file,bbox_extra_artists=(lgd,), bbox_inches='tight')
#         else:
#             plt.savefig(out_file);

#         plt.close();
#     else:
#         plt.show()  