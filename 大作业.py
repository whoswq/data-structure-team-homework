"""
细菌繁殖的简单模拟，忽略菌落的结构，仅从数量和行为特征两个方面进行模拟
有点大问题，这些方法如何与图形界面配合
"""
import numpy as np
from tkinter import *
import time
import os


class Bacteria():
    """
    细菌类
    """
    __num = 0  # 记录Bacteria类中实例数量
    rp_prob = 0.8  # 记录Bacteria实例达到分裂条件时的分裂概率

    def __init__(self, lifetime=20, hunger=3, tig=3):
        self.lifetime = lifetime  # 细菌寿命
        self.hunger = hunger  # 饥饿值
        self.tig = tig  # 分裂的触发条件
        Bacteria.__num += 1  # 当创建实例时，记录数量的__num加一

    def __del__(self):
        """
        定义了实例被删除时的行为
        """
        if Bacteria.__num >= 0:
            Bacteria.__num -= 1  # 被删除时__num减一
        else:
            raise ValueError("Bacteria类__del__")

    def can_divide(self):
        if self.hunger > self.tig:
            return True
        else:
            return False

    @classmethod
    def get_num(cls):
        return Bacteria.__num

    @classmethod
    def set_rp_prob(cls, prob=0.5):
        Bacteria.rp_prob = prob


class Food():
    """
    食物类
    """
    __num = 0  # 记录Food实例数量

    def __init__(self, lifetime=40):
        Food.__num += 1
        self.lifetime = lifetime  # Food实例的寿命

    def __del__(self):
        """
        定义了实例被删除时的行为
        """
        if Food.__num >= 0:
            Food.__num -= 1
        else:
            raise ValueError("Food类__del__")

    @classmethod
    def get_num(cls):
        return Food.__num


class Field():
    """
    表示一块可供细菌活动的区域，要求此类有且仅有一个实例
    """
    __food_gen_prob = 0.6
    __food_gen_corr = 0.05  # 食物产生概率与周围食物数量之间的关系
    __food_distribution = None  # 记录食物产生概率的列表
    size = 0
    __food_num = []  # 记录每次更新之后食物的数量
    __bacteria_num = []  # 记录每次更新之后细菌的数量
    __direction = {
        0: (0, 1),
        1: (-1, 1),
        2: (-1, 0),
        3: (-1, -1),
        4: (0, -1),
        5: (1, -1),
        6: (1, 0),
        7: (1, 1)
    }

    def __init__(self, n, mood="plain"):
        """
        n代表了区域是一个(n, n)大小的二维区域
        初始化时默认区域中全部是食物
        在初始化时更新所有的类变量，即使删除了实例，类中的数据也会被保存
        期待着通过mood这个参数调节食物的分布规律
        """
        Field.set_food_gen_corr()
        Field.set_food_gen_prob()
        Field.clear_bacteria_num()
        Field.clear_food_num()
        self.__size = n
        Field.size = n
        self.__state = [[Food() for i in range(n)] for i in range(n)]
        # 这是最重要的属性之一
        if mood == "plain":
            # 设置食物的分布规律
            Field.__food_distribution = [
                [Field.__food_gen_prob for i in range(n)] for j in range(n)
            ]

    def __str__(self):
        """
        调试的时候用一用
        """
        return str(self.transform())

    def set_bacteria(self, coordinate=(0, 0)):
        """
        设置细菌的初始位置，每次执行只能设置一个细菌的位置
        """
        i, j = coordinate
        if i < self.__size and j < self.__size:
            old = self.__state[i][j]
            self.__state[i][j] = Bacteria()
            del old
        else:
            raise IndexError("Filed.set_bacteria()设置位置超过了区域大小")

    def evolution(self, coordinate):
        """
        选取区域中的一个位置coordinate，分析这里可能发生的情况
        分为三类，食物、空地、细菌
        """
        i, j = coordinate[0], coordinate[1]
        if i < self.__size and j < self.__size:
            old = self.__state[i][j]  # 取出i, j位置的对象的引用
            if isinstance(old, Food):  # 判断这个位置是否是食物
                if old.lifetime == 1:  # 如果食物寿命为1，会被销毁
                    self.__state[i][j] = None
                    del old  # 删除food的引用，此时Food类中记录实例数量的变量减一
                else:
                    old.lifetime -= 1  # 如果食物寿命大于1，寿命减一
            elif isinstance(old, Bacteria):
                # 如果是细菌，考虑细菌向周围运动，同时也要考虑细菌的死亡情况
                empty_pos = []
                food_pos = []
                for x in range(8):  # 注意i, j已经用过了
                    direction = Field.__direction[x]
                    position = i + direction[0], j + direction[1]
                    if not Field.out_of_range(Field.size, position):
                        sur = self.__state[position[0]][position[1]]
                        # 分析周围环境
                        if isinstance(sur, Food):
                            food_pos.append(position)
                        elif isinstance(sur, Bacteria):
                            continue
                        elif sur is None:
                            empty_pos.append(position)
                        else:
                            raise Exception("Field.evolution()未知错误")

                def move_bacteria(old):
                    """
                    描述了细菌不分裂时的行为
                    """
                    num_food = len(food_pos)
                    num_empty = len(empty_pos)
                    move_prob = (num_empty + 1) / (num_empty + num_food + 1)
                    r = np.random.random_sample()
                    if food_pos != [] and r > move_prob:  # 如果周围有食物
                        old.hunger += 1
                        nxt_pos = food_pos[np.random.randint(len(food_pos))]
                        food = self.__state[nxt_pos[0]][nxt_pos[1]]
                        self.__state[i][j] = None
                        self.__state[nxt_pos[0]][nxt_pos[1]] = old
                        del food
                    else:
                        old.hunger -= 1
                        empty = [(i, j)] + empty_pos
                        nxt_pos = empty[np.random.randint(len(empty))]
                        self.__state[i][j] = None
                        self.__state[nxt_pos[0]][nxt_pos[1]] = old

                # 下面要讨论细菌面对空位和食物的具体选择问题，这时候会包含细菌的分裂
                # 首先讨论寿命只剩1的情况，销毁这个细菌就行
                if old.lifetime == 1:
                    self.__state[i][j] = None
                    del old
                else:
                    old.lifetime -= 1  # 如果寿命不是1，寿命减一
                    if old.hunger == 1:  # 讨论饥饿值
                        # 首先是饥饿值仅剩1的情况
                        if food_pos == []:  # 周围没有食物，会被饿死
                            self.__state[i][j] = None
                            del old
                        else:
                            nxt = food_pos[np.random.randint(
                                len(food_pos))]  # 随机挑选一个位置
                            food = self.__state[nxt[0]][nxt[1]]
                            old.hunger += 1
                            self.__state[nxt[0]][nxt[1]] = old
                            # 将被选中食物所占的位置替换为原来的细菌
                            self.__state[i][j] = None
                            del food  # 删除被吃食物的引用，食物总数减一
                    elif old.hunger > old.tig:
                        # 当饥饿值大于设定值，触发分裂条件，有一定概率分裂
                        r = np.random.random_sample()
                        if r < Bacteria.rp_prob and empty_pos != []:  # 判断是否分裂
                            old.hunger -= 1
                            new_bac = Bacteria()
                            new_pos = empty_pos[np.random.randint(
                                len(empty_pos))]
                            self.__state[new_pos[0]][new_pos[1]] = new_bac
                        else:
                            move_bacteria(old)
                    else:
                        # 剩余的情况，只有向空位移动或者吃食物
                        move_bacteria(old)

            elif old is None:
                # 如果是空地，我们考虑产生食物
                food_cnt = 0
                for y in range(8):
                    direction = Field.__direction[y]
                    position = i + direction[0], j + direction[1]
                    if not Field.out_of_range(Field.size, position):
                        if isinstance(self.__state[position[0]][position[1]],
                                      Food):
                            food_cnt += 1  # 统计相邻区域食物的数量
                probability = Field.__food_distribution[i][
                    j] + Field.__food_gen_corr * food_cnt  # 产生食物的概率
                r = np.random.random_sample()
                if r <= probability:
                    self.__state[i][j] = Food()
            else:
                raise Exception("Field.evolution()未知错误")
        else:
            raise IndexError("Field.evolution()选取位置超过区域大小")

    def transform(self):
        """
        将self.__state的数据转化为容易识别的数据
        """
        list_output = [[] for i in range(Field.size)]
        for x in range(Field.size):
            for y in range(Field.size):
                now = self.__state[x][y]
                if isinstance(now, Food):
                    list_output[x].append(0)
                elif isinstance(now, Bacteria):
                    list_output[x].append(1)
                elif now is None:
                    list_output[x].append(None)
        return list_output

    def update(self):
        """
        执行一次算作对于状态的一次更新，返回一个由0，1，None组成的二维列表
        """
        cnt = 0
        while cnt < Field.size**2:
            i, j = np.random.randint(0, Field.size), np.random.randint(
                0, Field.size)
            self.evolution((i, j))
            cnt += 1
        Field.__bacteria_num.append(Bacteria.get_num())
        Field.__food_num.append(Food.get_num())
        return self.transform()

    @staticmethod
    def out_of_range(size, pos):
        if (pos[0] < size and pos[0] >= 0) and (pos[1] < size and pos[1] >= 0):
            return False
        else:
            return True

    @classmethod
    def set_food_gen_prob(cls, prob=0.2):
        Field.__food_gen_prob = prob

    @classmethod
    def get_food_gen_prob(cls):
        return Field.__food_gen_prob

    @classmethod
    def set_food_gen_corr(cls, corr=0.05):
        Field.__food_gen_corr = corr

    @classmethod
    def get_food_gen_corr(cls):
        return Field.__food_gen_corr

    @classmethod
    def clear_food_num(cls):
        Field.__food_num = []

    @classmethod
    def get_food_num_list(cls):
        return Field.__food_num

    @classmethod
    def clear_bacteria_num(cls):
        Field.__bacteria_num = []

    @classmethod
    def get_bacteria_num_list(cls):
        return Field.__bacteria_num


if __name__ == "__main__":
    """list_b = []
    for i in range(10):
        list_b.append(Bacteria())
    rb = list_b[0]
    list_b[0] = None  一定要注意怎么实现对于实例的删除！！！
    del rb
    print(list_b)
    print("bacteria 数量：", Bacteria.get_num()) """
    field = Field(15)
    for i in range(5):
        x = np.random.randint(0, 10)
        y = np.random.randint(0, 10)
        field.set_bacteria((x, y))
    root = Tk()
    root.title('细菌繁殖的简单模拟')
    frame1 = LabelFrame(root, text='模拟图像')
    frame2 = LabelFrame(root, text='设置')
    frame1.grid(column=0, row=0, columnspan=10, rowspan=10, padx=10, pady=10)
    frame2.grid(column=11, row=0, columnspan=10, rowspan=10)
    Label(frame2, text='图像行数').grid(column=11, row=0)
    Label(frame2, text='图像列数').grid(column=11, row=1)
    row1 = Entry(frame2)
    row1.grid(column=12, row=0)
    column1 = Entry(frame2)
    column1.grid(column=12, row=1)
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
        rowdata = int(row1.get())
        columndata = int(column1.get())
        coldtimedata = float(coldtime.get())
        totaltime = float(time1.get())
        time2 = int(totaltime / coldtimedata)
        while n <= time2:
            n = n + 1
            getlist = field.update()
            frame1.update()
            p = 0
            q = 0
            for i in range(columndata):
                for j in range(rowdata):
                    if getlist[i][j] == 0:
                        Label(frame1, text="*", fg='blue').grid(column=i,
                                                                row=j)
                        q = q + 1
                    elif getlist[i][j] == 1:
                        Label(frame1, text="#", fg='black').grid(column=i,
                                                                 row=j)
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
        rowdata = int(row1.get())
        columndata = int(column1.get())
        if count % 2 == 1:
            for i in range(columndata):
                for j in range(rowdata):
                    if getlist[i][j] == 0:
                        Label(frame1, text="*", fg='blue').grid(column=i,
                                                                row=j)
                    elif getlist[i][j] == 1:
                        Label(frame1, text="#", fg='black').grid(column=i,
                                                                 row=j)
                    else:
                        Label(frame1, text=" ").grid(column=i, row=j)
            os.system("pause")

    Button(frame2, text="确定", command=sett).grid(column=12, row=6)
    Button(frame2, text="暂停", command=stop).grid(column=13, row=6)
    root.mainloop()
