import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate

x = [6, 6.2, 6.6, 7, 8, 8.5, 9, 9.5, 10, 10, 10]
y = [0, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]
plt.xlim(12, 0)
tck = interpolate.CubicSpline(y, x)

y_plot = np.linspace(0, 90, 300)
plt.plot(tck(y_plot), y_plot)
plt.show()