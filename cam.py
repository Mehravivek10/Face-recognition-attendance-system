import cv2

cap = cv2.VideoCapture(0)  # Use 1 if you have an external camera
cap.set(3, 1280)  # Width
cap.set(4, 720)   # Height

if not cap.isOpened():
    print("Error: Cannot access the camera")
    exit()

while True:
    success, img = cap.read()  # Capture frame
    if not success:
        print("Error: Failed to capture frame")
        break

    # Display the captured frame
    cv2.imshow("Face attendance", img)

    # Exit the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
