import matplotlib.pyplot as plt
import numpy as np
data = np.random.randint(0, 100, 100)

fig, ax = plt.subplots()
ax.hist(data, bins=10)

def onclick(event):
    width = ax.patches[0].get_width()
    start = ax.patches[0].get_x()
    end = start + width * 10  # Полагаем 10 попаа
    if event.xdata is not None and event.inaxes == ax:
        if event.xdata < start:
            new_xlim = (event.xdata, end)
        elif event.xdata > end:
            new_xlim = (start, event.xdata)
        else:
            return
        plt.xlim(new_xlim)
        plt.draw()

cid = fig.canvas.mpl_connect('button_press_event', onclick)
plt.show()