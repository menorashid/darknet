import os
import sys
# matplotlib.use('TkAgg')
from helpers import util
# , visualize
import numpy as np
# import cv2
import get_video_results as gvr
# from Tkinter import *
import Tkinter as tk
import tkFileDialog
import glob
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


    def choose_file(self):
        vid_file = tkFileDialog.askopenfilename(parent = self, title = 'Choose mp4 file')
        vid_file = self.check_vid_file(vid_file)
        if vid_file is None:
            error_msg = 'Please select valid format file\n'
            error_msg = error_msg+ ','.join(self.acceptable_formats)+' are valid.'
            self.start_state(error_msg = error_msg)
        else:
            self.file_to_process = vid_file
            self.process_state()
    



    def select_state(self):
        self.empty_last_state()
        # list_choices = [str(val) for val in range(10)]
        # list_choices = 


        self.canvas = tk.Canvas(self,
            # width = self.winfo_width(), height = self.winfo_height())
            width = self.glob_width-100, height = self.glob_height-100)
        self.listbox = CheckListBox(self.canvas,self.files_to_process, bd=1, relief='sunken', background='white')


        self.canvas.pack(side=tk.LEFT)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.listbox, anchor="nw")

        # self.update()
        if self.listbox.winfo_height()>=(self.glob_height-100):

            self.vertscroll = tk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
            self.vertscroll.pack(side=tk.RIGHT, fill=tk.Y)
            self.update()
            bbox= self.canvas.bbox(tk.ALL)
            self.canvas.configure(yscrollcommand=self.vertscroll.set)
            self.bind('<Configure>', self.onFrameConfigure)

        if self.listbox.winfo_width()>=(self.glob_width-100):

            self.horiscroll = tk.Scrollbar(self, orient='horizontal', command=self.canvas.xview)
            self.horiscroll.pack(side=tk.BOTTOM, fill=tk.X)
            self.update()
            bbox= self.canvas.bbox(tk.ALL)
            self.canvas.configure(yscrollcommand=self.horiscroll.set)
            self.bind('<Configure>', self.onFrameConfigure)

        cont_btn = tk.Button(self)
        cont_btn['text'] = 'Continue'
        cont_btn['fg']   = 'Black'
        cont_btn['command'] = self.start_state
        cont_btn.pack()

        self.cont_btn = cont_btn
        self.back_btn = self.back_button('select').pack()

    def process_state(self):
        self.empty_last_state()
        vid_name = os.path.split(self.vid_file)[1]
        label_msg = 'Processing '+vid_file
        tk.Label(self,text = label_msg).pack()
        self.back_btn = self.back_button('select').pack()
        self.exit_btn = self.exit_button().pack()
        cont_btn = tk.Button(self)
        cont_btn['text'] = 'Continue'
        cont_btn['fg']   = 'Black'
        cont_btn['command'] = self.start_state
        cont_btn.configure(state=DISABLED)
        cont_btn.pack()

        self.cont_btn = cont_btn
        self.back_btn = self.back_button('select').pack()


    def onFrameConfigure(self,event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    

    

    def back_button(self,state_str):
        exit_btn = tk.Button(self)
        exit_btn['text'] = 'Back'
        exit_btn['fg']   = 'Black'
        exit_btn['command'] =  self.start_state
        return exit_btn

    def exit_button(self):
        exit_btn = tk.Button(self)
        exit_btn['text'] = 'Exit'
        exit_btn['fg']   = 'Black'
        exit_btn['command'] =  self.quit
        return exit_btn

    def empty_last_state(self):
        widgets = self.winfo_children()
        for w in widgets:
            w.destroy()

        

    def start_state(self, error_msg = None):
        self.empty_last_state()
        label_msg = 'Welcome to Face Finder'
        tk.Label(self,text = label_msg).pack()
        if error_msg is not None:
            tk.Label(self,text = error_msg, fg ='red').pack()
        self.upload_btn = tk.Button(self)
        self.upload_btn['text'] = 'Choose Video File'
        self.upload_btn['fg']   = 'Black'
        self.upload_btn['command'] =  self.choose_file
        self.upload_btn.pack()

        self.exit_btn = self.exit_button()
        self.exit_btn.pack()

        

    def __init__(self, master, glob_height = 500, glob_width = 500):
        # master=None):
        # self = tk.Tk()
        tk.Frame.__init__(self, master,width = glob_width, height = glob_height)
        
        # '500x500'
        
        self.glob_height = glob_height
        self.glob_width = glob_width
        self.acceptable_formats = ['.mp4','.MP4']
        self.files_to_process = []
        self.pack()
        self.start_state()

def main():
    root = tk.Tk()
    root.geometry('500x500')
    app = Application(master = root)
    app.mainloop()
    # root.destroy()


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