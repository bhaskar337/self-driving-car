# import numpy as np
# import cv2
from matplotlib import pyplot as plt

# # img =  cv2.imread('image.png', 0)
# # img_l = img[:int(img.shape[0]/2),:]
# # img_r = img[int(img.shape[0]/2)+1:,:]

# img_l = cv2.imread('0_c.jpg', 0)
# img_r = cv2.imread('0_r.jpg', 0)

# # stereo = cv2.StereoSGBM_create(numDisparities=16, blockSize=15)
# window_size = 3
# min_disp = 16
# num_disp = 112-min_disp
# stereo = cv2.StereoSGBM_create(
#     minDisparity = min_disp,
#     numDisparities = num_disp,
#     blockSize = 16,
#     P1 = 8*3*window_size**2,
#     P2 = 32*3*window_size**2,
#     disp12MaxDiff = 1,
#     uniquenessRatio = 10,
#     speckleWindowSize = 100,
#     speckleRange = 32
# )
# disparity = stereo.compute(img_l, img_r)
# plt.imshow(disparity, 'gray')
# plt.show()

import cv2
import numpy as np
 
# disparity settings
window_size = 5
min_disp = 32
num_disp = 112-min_disp
stereo = cv2.StereoSGBM_create(
    blockSize = 16,
    minDisparity = min_disp,
    numDisparities = num_disp,
    uniquenessRatio = 10,
    speckleWindowSize = 100,
    speckleRange = 32,
    disp12MaxDiff = 1,
    P1 = 8*3*window_size**2,
    P2 = 32*3*window_size**2,
)
 
# morphology settings
kernel = np.ones((12,12),np.uint8)
 
counter = 450
 
while counter < 650:
 
    # increment counter
    counter += 1
 
    # only process every third image (so as to speed up video)
    if counter % 3 != 0: continue
 
    # load stereo image
    filename = str(counter).zfill(4)
 
    image_left = cv2.imread('0_c.jpg')
    image_right = cv2.imread('0_r.jpg')
 
    # compute disparity
    disparity = stereo.compute(image_left, image_right).astype(np.float32) / 16.0
    disparity = (disparity-min_disp)/num_disp


threshold = cv2.threshold(disparity, 0.6, 1.0, cv2.THRESH_BINARY)[1]
morphology = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)
# cv2.imshow('left eye', image_left)
# cv2.imshow('right eye', image_right)
# cv2.imshow('disparity', disparity)
# cv2.imshow('threshold', threshold)
# cv2.imshow('morphology', morphology)
# cv2.waitKey(1)
plt.imshow(disparity, 'gray')
plt.show()
