# x_[t+1] = x[t] + v[t] * cos(psi[t]) * dt
# y_[t+1] = y[t] + v[t] * sin(psi[t]) * dt
# psi_[t+1] = psi[t] + v[t] / Lf * delta[t] * dt
# v_[t+1] = v[t] + a[t] * dt




# from scipy import interpolate
# import matplotlib.pyplot as plt

# car_d = 6
# pts_x = [car_d, car_d+4, car_d+4, car_d+4]
# pts_y = [0, 30, 60, 90]
# tck = interpolate.splrep(pts_y, pts_x)


# d = []
# for dist in range(-5, 61):
# 	d.append(float(interpolate.splev(dist, tck)))

# plt.plot(d, list(range(-5, 61)))
# plt.axis([0, 30, -5, 60])
# plt.show()