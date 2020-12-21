from tkinter import *
import time
import os
from main import Field
import numpy as np


root = Tk()
root.title('细菌繁殖的简单模拟')
frame1 = LabelFrame(root, text='模拟图像')
frame2 = LabelFrame(root, text='设置')
frame1.grid(column=0, row=0, columnspan=10, rowspan=10, padx=10, pady=10)
frame2.grid(column=11, row=0, columnspan=10, rowspan=10)
Label(frame2, text='图像大小').grid(column=11, row=0)
row1 = Entry(frame2)
row1.grid(column=12, row=0)
Label(frame2, text="刷新时间").grid(column=11, row=2)
coldtime = Entry(frame2)
coldtime.grid(column=12, row=2)
Label(frame2, text="秒").grid(column=13, row=2)
Label(frame2, text="总时间").grid(column=11, row=3)
time1 = Entry(frame2)
time1.grid(column=12, row=3)
Label(frame2, text="秒").grid(column=13, row=3)
num1 = IntVar()
num2 = IntVar()
Label(frame2, text="细菌个数").grid(column=11, row=4)
Label(frame2, textvariable=num1).grid(column=12, row=4)
Label(frame2, text="食物个数").grid(column=11, row=5)
Label(frame2, textvariable=num2).grid(column=12, row=5)
global count
count = 0
global m
m = 0


def sett():
    global getlist
    global n
    global m
    n = 0
    if m != 0:
        n = m
    size = int(row1.get())
    coldtimedata = float(coldtime.get())
    totaltime = float(time1.get())
    time2 = int(totaltime / coldtimedata)

    field = Field(size)
    for i in range(size//10):
        x = np.random.randint(0, size)
        y = np.random.randint(0, size)
        field.set_bacteria((x, y))

    while n <= time2:
        n = n + 1
        getlist = field.update()
        frame1.update()
        p = 0
        q = 0
        for i in range(size):
            for j in range(size):
                if getlist[i][j] == 0:
                    Label(frame1, text="*", fg='blue').grid(column=i, row=j)
                    q = q + 1
                elif getlist[i][j] == 1:
                    Label(frame1, text="#", fg='black').grid(column=i, row=j)
                    p = p + 1
                else:
                    Label(frame1, text=" ").grid(column=i, row=j)
        num1.set(p)
        num2.set(q)
        time.sleep(coldtimedata)
    m = 0


def stop():
    global count
    count = count + 1
    size = int(row1.get())
    size = int(column1.get())
    if count % 2 == 1:
        for i in range(size):
            for j in range(size):
                if getlist[i][j] == 0:
                    Label(frame1, text="*", fg='blue').grid(column=i, row=j)
                elif getlist[i][j] == 1:
                    Label(frame1, text="#", fg='black').grid(column=i, row=j)
                else:
                    Label(frame1, text=" ").grid(column=i, row=j)
        os.system("pause")


Button(frame2, text="确定", command=sett).grid(column=12, row=6)
Button(frame2, text="暂停", command=stop).grid(column=13, row=6)
root.mainloop()