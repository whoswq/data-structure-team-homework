import numpy as np
import matplotlib.pylab as plt
import pickle


class Bacteria():
    """
    bacteria类
    可以认为这是对会繁殖、会运动、有寿命、会饿死的捕食者的模拟
    """
    __num = 0  # 记录Bacteria类中实例数量
    rp_prob = 0.6  # 记录Bacteria实例达到分裂条件时的分裂概率
    __lifetime = 40  # 记录Bacteria类实例的寿命
    __hunger = 1  # 记录Bacteria类中实例的默认饥饿值
    __tig = 5  # 记录Bacteria类中实例的分裂触发值

    def __init__(self):
        self.lifetime = Bacteria.__lifetime  # bacteria寿命
        self.hunger = Bacteria.__hunger  # 饥饿值
        self.tig = Bacteria.__tig  # 分裂的触发条件
        Bacteria.__num += 1  # 当创建实例时，记录数量的__num加一

    def __del__(self):
        """
        定义了实例被删除时的行为
        """
        if Bacteria.__num >= 0:
            Bacteria.__num -= 1  # 被删除时__num减一
        else:
            raise ValueError("Bacteria.__del__()类中没有实例")

    def can_divide(self):
        return self.hunger > self.tig

    @classmethod
    def get_num(cls):
        return Bacteria.__num

    @classmethod
    def set_lifetime(cls, lifetime):
        """设置寿命"""
        Bacteria.__lifetime = lifetime

    @classmethod
    def set_hunger(cls, hunger):
        """设置饥饿值"""
        Bacteria.__hunger = hunger

    @classmethod
    def set_tig(cls, tig):
        """设置分裂触发值"""
        Bacteria.__tig = tig


class Food():
    """
    food类
    考虑food是一种会运动、会繁殖的生物，会吃东西，有饥饿值
    """
    __num = 0  # 记录Food实例数量
    rp_prob = 0.9  # 记录Food类实例的繁殖概率
    __lifetime = 20  # 记录Food类实例的寿命
    __hunger = 1  # 记录Food类实例的饥饿值
    __tig = 2  # 记录Food实例的繁殖触发值

    def __init__(self):
        Food.__num += 1
        self.hunger = Food.__hunger
        self.tig = Food.__tig  # food繁殖的触发条件，一般考虑food繁殖能力强，此值默认比较小
        self.lifetime = Food.__lifetime  # Food实例的寿命

    def __del__(self):
        if Food.__num >= 0:
            Food.__num -= 1
        else:
            raise ValueError("Food.__del__()类中没有实例")

    def can_divide(self):
        return self.hunger > self.tig

    @classmethod
    def get_num(cls):
        return Food.__num

    @classmethod
    def set_lifetime(cls, lifetime):
        Food.__lifetime = lifetime

    @classmethod
    def set_hunger(cls, hunger):
        Food.__hunger = hunger

    @classmethod
    def set_tig(cls, tig):
        Food.__tig = tig


class Field():
    """
    表示一块可供bacteria活动的区域，要求此类有且仅有一个实例
    """
    # 以下参数的设置都在类方法中完成
    __grass_growth_list = []  # 记录“草”的增长模式，二维列表，每一格存储“草”的增长速率
    # 希望可以设计出除了平均分布以外的分布
    __average_rate = 0  # 记录平均增长时增长速率
    __max_grass = float("inf")
    size = 0
    __food_num = []  # 记录每次更新之后food的数量
    __bacteria_num = []  # 记录每次更新之后bacteria的数量
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

    def __init__(self, n, mode="plain", grass_i=5):
        """
        n: 区域大小，表示这是一个(n, n)的区域

        考虑了food和bacteria都有运动能力并且可以繁殖
        food要依靠吃“草”来生活
        在初始化时更新所有的类变量

        期待着通过mode这个参数调节food的分布规律
        """
        Field.clear_bacteria_num()
        Field.clear_food_num()
        Field.set_average_rate()
        self.__size = n
        Field.size = n
        self.__state = [[None for i in range(n)] for i in range(n)]  # 初始化构造空区域
        # 需要调用set_food与set_bacteria向区域中加入food和bacteria
        if mode == "plain":
            # 设置草的分布规律，草另行储存
            Field.plain_mode()  # 这个构造了草的增长速率列表
            self.__grass = [[grass_i for i in range(n)] for j in range(n)]
            # grass是food的food，此属性储存了当前区域grass数量分布

    def __str__(self):
        """
        调试的时候用一用
        """
        return str(self.transform())

    def set_bacteria(self, coordinate=(0, 0)):
        """
        设置bacteria初始位置，每次执行只能设置一个bacteria的位置
        """
        i, j = coordinate
        if i >= self.__size or j >= self.__size:
            raise IndexError("Field.set_bacteria()设置位置超过了区域大小")

        old = self.__state[i][j]
        self.__state[i][j] = Bacteria()
        del old

    def set_food(self, coordinate):
        """
        设置food初始位置，每次执行只能设置一个food位置
        """
        i, j = coordinate
        if i >= self.__size or j >= self.__size:
            raise IndexError("Field.set_food()设置位置超过了区域大小")
        old = self.__state[i][j]
        self.__state[i][j] = Food()
        del old

    def evolution(self, coordinate):
        """
        选取区域中的一个位置coordinate，分析这里可能发生的情况
        分为三类，food、bacteria、空地
        注意只要是food没有吃grass，grass就会增加
        """
        i, j = coordinate[0], coordinate[1]
        if i >= self.__size or j >= self.__size:
            raise IndexError("Field.evolution()选取位置超过区域大小")

        old = self.__state[i][j]  # 取出i, j位置的对象的引用

        if isinstance(old, Food):  # 如果是food
            empty_pos = []  # 储存附近有grass的空地，表示这是food可以去的空地

            food_pos = []  # 储存附近的food
            for d in range(8):
                direction = Field.__direction[d]
                position = i + direction[0], j + direction[1]
                if not Field.out_of_range(Field.size, position):
                    sur = self.__state[position[0]][position[1]]
                    if sur is None:
                        if self.__grass[position[0]][position[1]] > 0:
                            empty_pos.append(position)
                    elif isinstance(sur, Food):
                        food_pos.append(position)
            if self.__grass[i][j] > 0:
                empty_pos.append(coordinate)  # food有可能不动

            def move_food(old):
                """描述food在不分裂时的行为，假设food所在的地方grass不生长
                同时假设food只会向有grass的地方前进"""
                old.lifetime -= 1  # 寿命减1
                if empty_pos == []:  # 表示周围所有地方的草都没有了，待在原地
                    if self.__grass[i][j] == 0:
                        old.hunger -= 1  # 如果被捕食者所处位置没有草，饥饿值减一
                    else:
                        self.__grass[i][j] -= 1
                else:
                    index = np.random.randint(len(empty_pos))  # 随机选取一个可行的方向
                    nxt_pos = empty_pos[index]  # 表示food下一步前进的位置
                    self.__state[i][j] = None
                    self.__state[nxt_pos[0]][nxt_pos[1]] = old
                    self.__grass[nxt_pos[0]][
                        nxt_pos[1]] -= 1  # 表示前去的那个地方grass被吃掉1
                    old.hunger += 1

            if old.lifetime == 1:
                self.__state[i][j] = None
                del old  # 删除food的引用，Food类中记录实例数量的变量减1
                self.grass_grow(coordinate)  # 没有food后，grass会生长
            elif old.hunger == 1:  # 如果饥饿值为1，要吃grass
                if empty_pos == []:  # 表示周围没有空位，此时被饿死
                    self.__state[i][j] = None
                    del old
                else:
                    move_food(old)
            elif old.hunger > 1:  # 饥饿值大于1，考虑分裂或者向其他方向运动，但都会吃grass
                if old.hunger > old.tig:  # 说明达到了分裂条件，有概率分裂
                    positions = empty_pos[:-1]  # 除了当前位置的有grass的所有相邻位置
                    if len(positions) == 0:  # 没有空间支持food繁殖
                        move_food(old)
                    else:
                        r = np.random.random_sample()
                        if r < Food.rp_prob:  # 此时表示可以繁殖
                            old.hunger -= 1
                            idx = np.random.randint(len(positions))
                            new_pos = positions[idx]
                            self.__state[new_pos[0]][new_pos[1]] = Food()
                            self.__grass[new_pos[0]][new_pos[1]] -= 1
                        else:
                            move_food(old)
                else:  # 未达到分裂条件，只能考虑运动，注意只能向没有Bactera的地方运动
                    move_food(old)
        elif isinstance(old, Bacteria):
            self.grass_grow(coordinate)
            # 如果是bacteria，考虑向周围运动，同时也要考虑bacteria的死亡情况
            empty_pos = []  # 表示空位的位置
            food_pos = []  # 表示food的位置
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
                """描述了bacteria不分裂时的行为"""
                num_food = len(food_pos)
                num_empty = len(empty_pos)
                move_prob = (num_empty + 1) / (num_empty + num_food + 1)
                r = np.random.random_sample()
                if food_pos != [] and r > move_prob:  # 如果周围有food
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

            # 下面要讨论bacteria面对空位和food的具体选择问题，这时候会包含bacteria的分裂
            if old.lifetime == 1:
                self.__state[i][j] = None
                del old
            else:
                old.lifetime -= 1  # 如果寿命不是1，寿命减一
                if old.hunger == 1:  # 讨论饥饿值
                    # 首先是饥饿值仅剩1的情况
                    if food_pos == []:  # 周围没有food，会被饿死
                        self.__state[i][j] = None
                        del old
                    else:
                        nxt = food_pos[np.random.randint(
                            len(food_pos))]  # 随机挑选一个位置
                        food = self.__state[nxt[0]][nxt[1]]
                        old.hunger += 1
                        self.__state[nxt[0]][nxt[1]] = old
                        # 将被选中food所占的位置替换为原来的bacteria
                        self.__state[i][j] = None
                        del food  # 删除被吃food的引用，food总数减一
                elif old.hunger > old.tig:
                    # 当饥饿值大于设定值，触发分裂条件，有一定概率分裂
                    r = np.random.random_sample()
                    if r < Bacteria.rp_prob and empty_pos != []:  # 判断是否分裂
                        new_bac = Bacteria()
                        old.hunger -= 1  # 这里的改动对结果影响十分大？
                        new_pos = empty_pos[np.random.randint(len(empty_pos))]
                        self.__state[new_pos[0]][new_pos[1]] = new_bac
                    else:
                        move_bacteria(old)
                else:
                    # 剩余的情况，只有向空位移动或者吃food
                    move_bacteria(old)

        elif old is None:
            # 如果是空地，我们只考虑grass增长
            self.grass_grow(coordinate)
        else:
            raise Exception("Field.evolution()未知错误")

    def transform(self):
        """
        将self.__state的数据转化为容易观察的数据
        food用0代表，bacteria用1代表
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

    def grass_grow(self, coordinate, max=5):
        """描述一个位置草的生长，写成函数用起来方便嘛"""
        i, j = coordinate
        if i >= self.__size or j >= self.__size:
            raise IndexError("Field.grass_grow()所选位置超出了区域范围")
        if self.__grass[i][j] < Field.__max_grass:
            self.__grass[i][j] += self.__grass_growth_list[i][j]

    def get_grass(self):
        """调试的时候用一用"""
        return self.__grass

    @staticmethod
    def out_of_range(size, pos):
        if (pos[0] < size and pos[0] >= 0) and (pos[1] < size and pos[1] >= 0):
            return False
        else:
            return True

    @classmethod
    def plain_mode(cls):  # 我的梦想是可以让草的增长实现一定的分布规律
        """平均增长列表的构造，注意要先调用set_average_rate()与设置size"""
        Field.__grass_growth_list = [[
            Field.__average_rate for i in range(Field.size)
        ] for i in range(Field.size)]

    @classmethod
    def set_average_rate(cls, rate=1):
        Field.__average_rate = rate

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

    @classmethod
    def get_grass_growth_list(cls):
        return Field.__grass_growth_list

    @classmethod
    def set_max_grass(cls, max_):
        Field.__max_grass = max_


if __name__ == "__main__":
    """调试的时候用一用"""
    size = 50
    field = Field(size)
    for i in range(size**2 // 10):
        x = np.random.randint(0, size - 1)
        y = np.random.randint(0, size - 1)
        field.set_bacteria((x, y))
    for i in range(size**2 // 10):
        x = np.random.randint(0, size - 1)
        y = np.random.randint(0, size - 1)
        field.set_food((x, y))
    for i in range(500):
        field.update()
        if i % 20 == 0:
            print("done%s" % i)
    list1 = open("food_num", "wb")
    pickle.dump(Field.get_food_num_list(), list1)
    list2 = open("bacteria_num", "wb")
    pickle.dump(Field.get_bacteria_num_list(), list2)
    plt.plot(Field.get_food_num_list(), label="food population")
    plt.plot(Field.get_bacteria_num_list(), label="bacteria population")
    plt.xlabel("time")
    plt.ylabel("numbers")
    plt.legend()
    plt.show()
