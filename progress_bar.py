from Tkinter import Button, Tk, HORIZONTAL

from ttk import Progressbar
import time
import threading

# def select_state(self):
#         self.empty_last_state()
#         # list_choices = [str(val) for val in range(10)]
#         # list_choices = 


#         self.canvas = tk.Canvas(self,
#             # width = self.winfo_width(), height = self.winfo_height())
#             width = self.glob_width-100, height = self.glob_height-100)
#         self.listbox = CheckListBox(self.canvas,self.files_to_process, bd=1, relief='sunken', background='white')


#         self.canvas.pack(side=tk.LEFT)
#         self.canvas_frame = self.canvas.create_window((0, 0), window=self.listbox, anchor="nw")

#         # self.update()
#         if self.listbox.winfo_height()>=(self.glob_height-100):

#             self.vertscroll = tk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
#             self.vertscroll.pack(side=tk.RIGHT, fill=tk.Y)
#             self.update()
#             bbox= self.canvas.bbox(tk.ALL)
#             self.canvas.configure(yscrollcommand=self.vertscroll.set)
#             self.bind('<Configure>', self.onFrameConfigure)

#         if self.listbox.winfo_width()>=(self.glob_width-100):

#             self.horiscroll = tk.Scrollbar(self, orient='horizontal', command=self.canvas.xview)
#             self.horiscroll.pack(side=tk.BOTTOM, fill=tk.X)
#             self.update()
#             bbox= self.canvas.bbox(tk.ALL)
#             self.canvas.configure(yscrollcommand=self.horiscroll.set)
#             self.bind('<Configure>', self.onFrameConfigure)

#         cont_btn = tk.Button(self)
#         cont_btn['text'] = 'Continue'
#         cont_btn['fg']   = 'Black'
#         cont_btn['command'] = self.start_state
#         cont_btn.pack()

#         self.cont_btn = cont_btn
#         self.back_btn = self.back_button('select').pack()


class MonApp(Tk):
    def __init__(self):
        Tk.__init__(self)


        self.btn = Button(self, text='Traitement', command=self.traitement)
        self.btn.grid(row=0,column=0)
        self.progress = Progressbar(self, orient=HORIZONTAL,length=100,  mode='determinate')


    def traitement(self):
        def real_traitement():
            self.progress.grid(row=1,column=0)
            # self.progress.start()
            for i in range(0,100,10):
                print i
                self.progress['value']=i
                time.sleep(2)
            # self.progress.stop()
            self.progress.grid_forget()

            self.btn['state']='normal'

        self.btn['state']='disabled'
        threading.Thread(target=real_traitement).start()
        print 'hello after thread'

if __name__ == '__main__':

    app = MonApp()
    app.mainloop()