from collections import deque
from PIL import ImageGrab
import time

import cv2
import numpy as np
from lane_detection.utils import get_lane_lines, smoothen_over_time, weighted_img


if __name__ == '__main__':
	# buffer to store lane lines of multiple frames
	lane_lines = deque(maxlen=10)

	while True:
		# grab the top left corner of the screen
	    screen = np.array(ImageGrab.grab(bbox=(0, 30, 640, 510)))
	    img_h, img_w = screen.shape[0], screen.shape[1]
	    
	    try:
	    	# detect lane lines
	        lane_lines.append(get_lane_lines(color_image=screen, solid_lines=True))
	    except:
	        pass

	    # smoothening to avoid flickering of lane lines
	    lane_line = smoothen_over_time(lane_lines)
	  
		# prepare empty mask on which lines are drawn
	    line_img = np.zeros(shape=(img_h, img_w))
	    # draw lanes found
	    for lane in lane_line:
	        lane.draw(line_img)

	    # blend the orignal image with the lines
	    img_color = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
	    img_blend = weighted_img(line_img, img_color, α=0.8, β=1., λ=0.)

	    cv2.imshow('window', img_blend)
	    
	    key = cv2.waitKey(1) & 0xFF
	    if key == ord("q"):
	        cv2.destroyAllWindows()
	        break