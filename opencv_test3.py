import numpy as np
import cv2

def nothing():
	pass

cap1 = cv2.VideoCapture('IMG_1996.MOV')
length = int(cap1.get(cv2.CAP_PROP_FRAME_COUNT))
cap2 = cv2.VideoCapture('IMG_1996.MOV')
for i in range(length/2):
	cap2.read()
cv2.namedWindow('image')
cv2.createTrackbar('dy', 'image', 0, 255, lambda _: _)
cv2.createTrackbar('threshold1', 'image', 0, 255, lambda _: _)
cv2.createTrackbar('threshold2', 'image', 0, 255, lambda _: _)
kernel = np.ones((5,5), np.uint8)

while(True):
	# Capture frame-by-frame
	ret, frame = cap1.read()

	# Our operations on the frame come here
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	dy = cv2.getTrackbarPos('dy', 'image')
	threshold1 = cv2.getTrackbarPos('threshold1', 'image')
	threshold2 = cv2.getTrackbarPos('threshold2', 'image')
	#edges = cv2.Canny(frame, dy, threshold1, threshold2)
	dst = cv2.cornerHarris(gray,2,3,0.04)

	#result is dilated for marking the corners, not important
	dst = cv2.dilate(dst,None)
	# Threshold for an optimal value, it may vary depending on the image.
	frame[dst>0.01*dst.max()]=[0,0,255]
	print type(dst>0.01*dst.max())
	#img_erosion = cv2.erode(edges, kernel, iterations=1)
	# Display the resulting frame
	ret2, frame2 = cap2.read()
	frame[:400,:400] = frame2[:400,:400]
	cv2.imshow('frame', frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# When everything done, release the capture
cap1.release()
cap2.release()
cv2.destroyAllWindows()