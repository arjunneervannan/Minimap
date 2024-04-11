import cv2

# Connect to capture device
cap = cv2.VideoCapture(2)

while True:
    ret, frame = cap.read()
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break

