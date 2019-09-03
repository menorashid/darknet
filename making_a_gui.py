import os
import sys
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from helpers.gui import Gui 
from helpers import util
# , visualize
import numpy as np
import sys
# import cv2
import get_video_results as gvr
# from Tkinter import *
import Tkinter as tk
from ttk import Progressbar
import tkFileDialog
import glob
import time
import threading
import multiprocessing
import subprocess
# import scipy.misc
from PIL import Image, ImageTk
# from tkFileDialog import askopenfilename

class CheckListBox(tk.Frame):
    def __init__(self, parent, choices, **kwargs):

        
        tk.Frame.__init__(self,parent,**kwargs)
        

        self.pack(side='left')

        
        self.vars = []
        bg = self.cget('background')
        for choice in choices:
            var = tk.StringVar(value=choice)
            self.vars.append(var)
            cb = tk.Checkbutton(self, var=var, text=choice,
                                onvalue=choice, offvalue='',
                                anchor='w',  background=bg,
                                relief='flat', highlightthickness=0
            )
            cb.pack(side='top', fill='x', anchor='w')


    def getCheckedItems(self):
        values = []
        for var in self.vars:
            value =  var.get()
            if value:
                values.append(value)
        return values


class Application(tk.Frame):


    def check_vid_file(self,vid_file):
        # vid_files_keep = []
        # for vid_file in vid_files:
        for af_curr in self.acceptable_formats:
            if vid_file.endswith(af_curr):
                return vid_file
                # vid_files_keep.append(vid_file)
                # break
        
        return None


    def choose_file(self,next_state):
        vid_file = tkFileDialog.askopenfilename(parent = self, title = 'Choose mp4 file')
        vid_file = self.check_vid_file(vid_file)
        if vid_file is None:
            error_msg = 'Please select valid format file. '
            error_msg = error_msg+ ','.join(self.acceptable_formats)+' are valid.'
            self.start_state(error_msg = error_msg)

        else:
            self.vid_file = vid_file
            self.make_dirs_etc()
            if next_state=='process_state':
                self.process_state()
            else:
                res_file = os.path.join(self.res_dir,'results_collated.npz')
                if os.path.exists(res_file):
                    self.analyze_plot()
                else:
                    error_msg = 'Please select video file with result.'
                    # res_file = os.path.split(res_file)
                    # res_file = os.path.join(os.path.split(res_file[0])[1],res_file[1])
                    # error_msg = error_msg+res_file+' not found'
                    self.start_state(error_msg = error_msg)
    
    def make_dirs_etc(self):
        vid_file = self.vid_file
        vid_name = os.path.split(vid_file)[1]
        self.vid_name = vid_name[:vid_name.rindex('.')] 
        self.data_dir = vid_file[:vid_file.rindex('.')]+self.frame_postpend
        util.mkdir(self.data_dir)
        self.res_dir = vid_file[:vid_file.rindex('.')]+self.result_postpend
        util.mkdir(self.res_dir)


    def process_state(self):
        self.empty_last_state()

        # self.vid_file = '../data/Cisi_kortsida.MP4'
        vid_name = os.path.split(self.vid_file)[1]
        label_msg = 'Processing '+vid_name

        tk.Label(self,text = label_msg,font = "Helvetica 16 bold").grid(row = 0, columnspan =3)
        
        self.progress_label = tk.Label(self, text = '')
        self.progress_label.grid(row=1,sticky = 'W',columnspan=3)
        self.back_btn = self.back_button('start')
        self.exit_btn = self.exit_button()
        
        self.back_btn.grid(row = 3,column = 1)
        self.exit_btn.grid(row = 3,column = 2)
        

        cont_btn = tk.Button(self)
        cont_btn['text'] = 'Analyze Plot'
        cont_btn['fg']   = 'Black'
        cont_btn['command'] = self.analyze_plot
        cont_btn.configure(state=tk.DISABLED)
        
        cont_btn.grid(row=3,column = 0)
        self.cont_btn = cont_btn
        
        self.progress = Progressbar(self, orient = tk.HORIZONTAL, length = self.glob_width, mode = 'determinate')
        self.progress.grid(row = 2,columnspan = 3)
        self.process_vid()

    def check_frame_extraction(self, data_dir, num_frames, post_pend, str_label):

        vid_name = os.path.split(self.vid_file)[1]
        vid_name = vid_name[:vid_name.rindex('.')]
        while self.extracting:
            saved = glob.glob(os.path.join(data_dir,vid_name+'_*[0-9]'+post_pend))
            num_saved = len(saved)
            num_done = min(100,num_saved/float(num_frames)*100)
            num_done_str = '%2d' % num_done
            self.progress_label.configure(text =  str_label+'. '+num_done_str+'% done.')
            self.progress.configure(value = num_done)
            time.sleep(1)
            self.update()

        num_done = 100
        num_done_str = '%2d' % num_done
        self.progress_label['text']= 'Extracting Frames. '+num_done_str+'% done.'
        self.progress['value']=num_done
        self.update()
    

    def get_frame_extraction_commands(self, out_dir):
        fps = self.fps
        vid_file = self.vid_file
        secs = gvr.get_duration(vid_file)
        inc_frames = fps/2.
        frame_times = list(np.arange(inc_frames, secs, fps))
        if (frame_times[-1]+fps)<secs:
            frame_times.append(frame_times[-1]+fps)

        commands = []
        for idx_time_curr,time_curr in enumerate(frame_times):
            commands.append( util.get_extract_image_command(vid_file, out_dir, time_curr, idx_time_curr+1))

        return commands

    def extracting_done(self, vals):
        self.extracting = False

    def process_vid(self):
        
        vid_file = self.vid_file
        vid_name = self.vid_name
        data_dir = self.data_dir
        res_dir = self.res_dir 

        self.extracting = True
        str_label = 'Extracting Frames'
        self.progress_label.configure(text = str_label)
        # ['text'] = str_label
        
        # vid_file[:vid_file.rindex('.')]+self.frame_postpend
        # util.mkdir(data_dir)

        
        # vid_file[:vid_file.rindex('.')]+self.result_postpend
        # util.mkdir(res_dir)
        
        self.update()

        
        commands = self.get_frame_extraction_commands(data_dir)
        num_frames = len(commands)


        subprocess.call('rm '+'"'+os.path.join(data_dir,'"*.jpg'),shell=True)
        self.extracting = True

        # time.sleep(1)

        pool = multiprocessing.Pool()
        pool.map_async(gvr.run_commandlines, commands, callback = self.extracting_done)
        self.check_frame_extraction(data_dir, num_frames,'.jpg',str_label)

        

        str_label = 'Running Detector'
        self.progress.configure(value = 0)
        self.progress_label.configure(text = str_label)
        self.update_idletasks()
        
        commands = []
        commands.append('rm '+'"'+os.path.join(res_dir,vid_name+'"_*[0-9].txt'))
        commands.append('rm '+'"'+os.path.join(res_dir,'results_collated."*'))
        commands.append('rm '+'"'+os.path.join(res_dir,'detections_over_time.jpg"'))
        
        for command in commands:
            subprocess.call(command,shell=True)
        
        self.extracting = True
        args = [(res_dir, data_dir, True)]
        pool = multiprocessing.Pool(1)
        pool.map_async(gvr.test_frames_gui, args, callback = self.extracting_done)
        self.check_frame_extraction(res_dir, num_frames,'.txt',str_label)
        
        # # det_confs, time, boxes = gvr.collate_results_for_plotting(res_dir, self.fps)

        self.progress_label.configure(text = 'Plotting')
        plt.ion()
        out_file_plot = gvr.plot_detections_over_time_new(vid_name, res_dir, self.fps)  
        out_file_plot = os.path.split(out_file_plot)
        out_file_plot = os.path.join(os.path.split(out_file_plot[0])[1],out_file_plot[1])

        # limit = 100
        # out_file_plot = [out_file_plot[idx_curr:idx_curr+limit] for idx_curr in range(0,len(out_file_plot),limit)]
        # out_file_plot = '\n'.join(out_file_plot)

        self.progress_label.configure(text = 'Plot saved at:\n'+out_file_plot)        
        self.cont_btn.configure(state=tk.NORMAL)
        plt.ioff()
        # print 'here'
        self.progress.destroy()
        self.back_btn.destroy()

        


    def analyze_plot(self):

        # vid_file = self.vid_file
        # vid_name = os.path.split(vid_file)[1]
        # vid_name = vid_name[:vid_name.rindex('.')]
        # res_dir = self.res_dir

        # vid_file = '../data/Cisi_kortsida.MP4'
        # res_dir = '../data/Cisi_kortsida_result_files_dummy'
        # frame_dir = '../data/Cisi_kortsida_frames_new'
        # util.mkdir(frame_dir)
        # fps = 5rm -
        # vid_name = 'Cisi_kortsida'
        # size_output = [416,416]
        res_file = os.path.join(self.res_dir,'results_collated.npz')
        gui = Gui(res_file,self.vid_file,self.fps,self.size_output, self.data_dir)
        raw_input()


    def onFrameConfigure(self,event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    

    

    def back_button(self,state_str):
        exit_btn = tk.Button(self)
        exit_btn['text'] = 'Back'
        exit_btn['fg']   = 'Black'
        if state_str=='start':
            exit_btn['command'] =  self.start_state

        return exit_btn

    def exit_button(self):
        exit_btn = tk.Button(self)
        exit_btn['text'] = 'Exit'
        exit_btn['fg']   = 'Black'
        exit_btn['command'] =  self.quit1
        return exit_btn

    def quit1(self):
        sys.exit(0)
        # print 'here'

    def empty_last_state(self):
        widgets = self.winfo_children()
        for w in widgets:
            w.destroy()
        self.update()
        

    def start_state(self, error_msg = None):
        self.empty_last_state()
        # tk.Label(root, 
        #  text="Green Text in Helvetica Font",
        #  fg = "light green",
        #  bg = "dark green",
        #  font = "Helvetica 16 bold italic").pack()

        label_msg = 'Welcome to Horse Face Finder'
        welcome_label = tk.Label(self,text = label_msg, font = "Helvetica 16 bold")
        # welcome_label.place(x=self.winfo_width()/2, y=self.winfo_height()/2, anchor="center")
        welcome_label.grid(row = 0,columnspan=3)
        # grid(row = 0,sticky='N')

        # pack()
        im = Image.open('horse.png')

        im = im.resize((self.glob_width-self.glob_width//4, self.glob_height -self.glob_height//3))

        # scipy.misc.imread('horse.png')
        # im = scipy.misc.imresize(im, (self.glob_height-50, self.glob_width-50))
        im = ImageTk.PhotoImage(im)
        # print im.shape

        label = tk.Label(self,image = im)
        label.image = im
        label.grid(row=1,columnspan=3)


        if error_msg is not None:
            tk.Label(self,text = error_msg, fg ='red').grid(row=2,columnspan=3)
        self.upload_btn = tk.Button(self)
        self.upload_btn['text'] = 'Process Video File'
        self.upload_btn['fg']   = 'Black'
        # self.next_state = 'process_state'
        self.upload_btn['command'] =  lambda: self.choose_file('process_state')
        self.upload_btn.grid(row=3,column=0)
        # pack()

        self.analyse_btn = tk.Button(self)
        self.analyse_btn['text'] = 'Analyse Video Result'
        self.analyse_btn['fg']   = 'Black'
        self.analyse_btn['command'] =   lambda: self.choose_file('analyze_plot')
        self.analyse_btn.grid(row=3,column=1)

        self.exit_btn = self.exit_button()
        self.exit_btn.grid(row=3, column = 2)
        # pack()

        

    def __init__(self, master, glob_height = 250, glob_width = 500):
        # master=None):
        # self = tk.Tk()
        tk.Frame.__init__(self, master,width = glob_width, height = glob_height)
        
        # '500x500'
        self.winfo_toplevel().title('Horse Face Finder')
        self.fps = 5
        self.size_output = [416,416]
        self.frame_postpend = '_frames'
        self.result_postpend = '_result_files'
        self.glob_height = glob_height
        self.glob_width = glob_width
        self.acceptable_formats = ['.mp4','.MP4']
        self.files_to_process = []
        self.pack()
        self.start_state()

def main():

    # vid_file = '../data/Cisi_kortsida.MP4'
    # res_dir = '../data/Cisi_kortsida_result_files'
    # frame_dir = '../data/Cisi_kortsida_frames_new'
    # util.mkdir(frame_dir)
    # fps = 5
    # vid_name = 'Cisi_kortsida'
    # size_output = [416,416]
    # res_file = os.path.join(res_dir,'results_collated.npz')
    # # gui = Gui(res_file,vid_file,fps,size_output, frame_dir)
    # # raw_input()

    # # pool = multiprocessing.Pool(1)
    # # [out_file] = pool.map(gvr.plot_detections_over_time_new, [(vid_name, res_dir, fps)])

    # out_file = gvr.plot_detections_over_time_new((vid_name, res_dir, fps))
    # print 'saved',out_file

    root = tk.Tk()
    root.geometry('500x250')
    app = Application(master = root)
    app.mainloop()
    root.destroy()


def progress_bar_code():
    pass

    # get total num frames
    # start checking thread
    # check if function returned 
    # or check if file saved
    # if saved increase progress bar
    # once done change label based on testing or plotting
    # print out file path
    # add visualize button
    # move to next window



if __name__=='__main__':
    main()