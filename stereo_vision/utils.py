import numpy as np
import cv2
from matplotlib import pyplot as plt

img =  cv2.imread('image.png', 0)
img_l = img[:int(img.shape[0]/2),:]
img_r = img[int(img.shape[0]/2)+1:,:]

# img_l = cv2.imread('left.jpg', 0)
# img_r = cv2.imread('right.jpg', 0)

# stereo = cv2.StereoSGBM_create(numDisparities=16, blockSize=15)
window_size = 3
min_disp = 16
num_disp = 112-min_disp
stereo = cv2.StereoSGBM_create(
    minDisparity = min_disp,
    numDisparities = num_disp,
    blockSize = 16,
    P1 = 8*3*window_size**2,
    P2 = 32*3*window_size**2,
    disp12MaxDiff = 1,
    uniquenessRatio = 10,
    speckleWindowSize = 100,
    speckleRange = 32
)
disparity = stereo.compute(img_l, img_r)
plt.imshow(disparity, 'gray')
plt.show()