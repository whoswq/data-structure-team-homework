import pickle
import matplotlib.pylab as plt

food = open("food_num", "rb")
list_food = pickle.load(food)
bacteria = open("bacteria_num", "rb")
list_bacteria = pickle.load(bacteria)
plt.plot(list_food, list_bacteria)
plt.xlabel("food")
plt.ylabel("bacteria")
plt.show()
