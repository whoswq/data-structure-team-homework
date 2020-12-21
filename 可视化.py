from mainnew import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from tkinter import *
import tkinter.messagebox

pause = False

root = Tk()
root.title('捕食者与被捕食者模型的模拟')
frame0 = LabelFrame(root, text='设置')
frame0.grid(row=0, column=0)
addr1 = StringVar(value=50)
Label(frame0, text='图像大小(大于70后运行会较慢').grid(row=0, column=0)
row1 = Entry(frame0, textvariable=addr1)
row1.grid(row=0, column=1)

#捕食者寿命、饥饿值、分裂触发值、达到分裂条件时的分裂概率默认值分别为40、1、5、0.6，可进行修改。
Label(frame0, text='捕食者寿命').grid(row=1, column=0)
addr2 = StringVar(value=40)
row2 = Entry(frame0, textvariable=addr2)
row2.grid(row=1, column=1)

Label(frame0, text='捕食者饥饿值').grid(row=2, column=0)
addr3 = StringVar(value=1)
row3 = Entry(frame0, textvariable=addr3)
row3.grid(row=2, column=1)

Label(frame0, text='捕食者分裂触发值').grid(row=3, column=0)
addr4 = StringVar(value=5)
row4 = Entry(frame0, textvariable=addr4)
row4.grid(row=3, column=1)

Label(frame0, text='捕食者分裂概率').grid(row=4, column=0)
addr5 = StringVar(value=0.6)
row5 = Entry(frame0, textvariable=addr5)
row5.grid(row=4, column=1)

#被捕食者寿命、饥饿值、分裂触发值、达到分裂条件时的分裂概率默认值为20、1、2、0.9，可进行修改。
Label(frame0, text='被捕食者寿命').grid(row=5, column=0)
addr6 = StringVar(value=20)
row6 = Entry(frame0, textvariable=addr6)
row6.grid(row=5, column=1)

Label(frame0, text='被捕食者饥饿值').grid(row=6, column=0)
addr7 = StringVar(value=1)
row7 = Entry(frame0, textvariable=addr7)
row7.grid(row=6, column=1)

Label(frame0, text='被捕食者繁殖触发值').grid(row=7, column=0)
addr8 = StringVar(value=2)
row8 = Entry(frame0, textvariable=addr8)
row8.grid(row=7, column=1)

Label(frame0, text='被捕食者繁殖概率').grid(row=8, column=0)
addr9 = StringVar(value=0.9)
row9 = Entry(frame0, textvariable=addr9)
row9.grid(row=8, column=1)

Label(frame0, text="草的最大容量").grid(row=9, column=0)
addr11 = StringVar(value="inf")
row11 = Entry(frame0, textvariable=addr11)
row11.grid(row=9, column=1)

#设置总更新次数(默认值为600次)
Label(frame0, text='总更新次数').grid(row=10, column=0)
addr10 = StringVar(value=600)
row10 = Entry(frame0, textvariable=addr10)
row10.grid(row=10, column=1)

frame1 = LabelFrame(root)
frame1.grid(row=0, column=1)
Label(frame1, text="开始后按空格暂停，再按恢复").pack()
num1 = IntVar()
num2 = IntVar()
Label(frame1, text="捕食者个数").pack()
Label(frame1, textvariable=num1).pack()
Label(frame1, text="被捕食者个数").pack()
Label(frame1, textvariable=num2).pack()


def sett():
    '''获取输入的参数设置值'''
    Bacteria.set_lifetime(float(row2.get()))
    Bacteria.set_hunger(float(row3.get()))
    Bacteria.set_tig(float(row4.get()))
    Bacteria.rp_prob = float(row5.get())
    Food.set_lifetime(float(row6.get()))
    Food.set_hunger(float(row7.get()))
    Food.set_tig(float(row8.get()))
    Food.rp_prob = float(addr9.get())
    totaltime = int(row10.get())
    size = int(row1.get())
    global field
    field = Field(size)
    Field.set_max_grass(float(addr11.get()))
    for i in range(size**2 // 5):
        x = np.random.randint(size)
        y = np.random.randint(size)
        field.set_food((x, y))
    for j in range(size**2 // 5):
        x = np.random.randint(size)
        y = np.random.randint(size)
        field.set_bacteria((x, y))

    def gen_position_list():
        """构造一个生成器，用于生成food和bacteria的坐标"""
        k = 0
        global pause
        while k <= totaltime:
            if not pause:
                k += 1
                field.update()
                lists = field.transform()
                food_position_x = []
                food_position_y = []
                bacteria_position_x = []
                bacteria_position_y = []
                n = len(lists)
                for i in range(n):
                    for j in range(n):
                        if lists[i][j] == 0:
                            food_position_x.append(i)
                            food_position_y.append(j)
                        elif lists[i][j] == 1:
                            bacteria_position_x.append(i)
                            bacteria_position_y.append(j)
                yield (food_position_x, food_position_y, bacteria_position_x,
                       bacteria_position_y, Field.get_food_num_list(),
                       Field.get_bacteria_num_list(), k,
                       len(bacteria_position_x), len(food_position_x))
            else:
                plt.pause(0.1)

    fig = plt.figure(1)
    ax1 = plt.subplot(1, 2, 1)
    ax2 = plt.subplot(1, 2, 2)
    ax2.set_xlabel("time")
    ax2.set_ylabel("number")
    f_x, f_y, b_x, b_y, f_num, b_num = [], [], [], [], [], []
    list_time = []
    f_number, = ax2.plot(list_time, f_num, label="food number")
    b_number, = ax2.plot(list_time, b_num, label="bacteria number")
    food = ax1.scatter(f_x,
                       f_y,
                       marker="o",
                       color="green",
                       s=25,
                       label="Food",
                       animated=True)
    bacteria = ax1.scatter(b_x,
                           b_y,
                           marker="o",
                           color="red",
                           s=25,
                           label="Bacteria",
                           animated=True)

    def init():
        ax1.set_xlim(0, size)
        ax1.set_ylim(0, size)
        ax2.set_xlim(0, 600)
        ax2.set_ylim(0, size**2)
        return food, bacteria, f_number, b_number

    def update(tp):
        f_x, f_y, b_x, b_y, f_num, b_num, i, f, b = tp
        list_time.append(i)
        food.set_offsets(list(zip(f_x, f_y)))
        bacteria.set_offsets(list(zip(b_x, b_y)))
        f_number.set_xdata(list_time)
        f_number.set_ydata(f_num)
        b_number.set_xdata(list_time)
        b_number.set_ydata(b_num)
        num1.set(f)
        num2.set(b)
        return food, bacteria, f_number, b_number

    def on_key_press(event):
        '''按空格键控制暂停和继续'''
        global pause
        if event.key == " ":
            if pause is False:
                pause = True
            elif pause is True:
                pause = False

    fig.canvas.mpl_connect('key_press_event', on_key_press)
    ani = FuncAnimation(fig,
                        update,
                        frames=gen_position_list,
                        init_func=init,
                        interval=30,
                        blit=True,
                        repeat=False)
    ax1.legend(bbox_to_anchor=(0.45, 1.02), loc=3)
    ax2.legend(loc="best")
    plt.show()


def delete():
    Field.clear_bacteria_num()
    Field.clear_food_num()
    global field
    del field
    global pause
    pause = False
    num1.set(0)
    num2.set(0)


def show_img():
    """显示捕食者与被捕食者之间的关系图，注意这里显示的永远是当前的数据而不是保存的数据"""
    food_num = Field.get_food_num_list()
    bact_num = Field.get_bacteria_num_list()
    if food_num != [] and bact_num != []:
        plt.plot([i for i in range(len(food_num))],
                 food_num,
                 label="prey")
        plt.plot([i for i in range(len(bact_num))],
                 bact_num,
                 label="predator")
        plt.xlabel("time")
        plt.ylabel("number")
        plt.title("varations of prey and predator number with time")
        # 塑料英语，不知这么写对不对
        plt.legend()
        plt.savefig("prey and predator number.pdf")
        plt.show()
    else:
        tkinter.messagebox.showwarning("警告", "未生成有效数据")


def fourier_transform():
    """这个有点问题，要不就不要了算了"""
    food_num = Field.get_food_num_list()
    bact_num = Field.get_bacteria_num_list()
    if food_num != [] and bact_num != []:
        average_bact = sum(bact_num) / len(bact_num)
        average_food = sum(food_num) / len(food_num)
        food_array = np.array(food_num) - average_food
        bact_array = np.array(bact_num) - average_bact
        food_spectrum = np.fft.fft(food_array)
        bact_spectrum = np.fft.fft(bact_array)
        plt.plot(food_spectrum, label="prey")
        plt.plot(bact_spectrum, label="predator")
        plt.xlabel("frequency")
        plt.ylabel("intensity")
        plt.legend()
        plt.savefig("transformed.pdf")
        plt.show()
    else:
        tkinter.messagebox.showwarning("警告", "未生成有效数据")
    """大失败，可能是数据过于不规律"""


Button(frame1, text="确定", command=sett).pack()
Button(frame1, text="清除数据", command=delete).pack()
Button(frame1, text="显示关系图", command=show_img).pack()
Button(frame1, text="Fourier变换", command=fourier_transform).pack()
root.mainloop()
