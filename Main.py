import os
import pickle
import cv2
import numpy as np
import face_recognition
import cvzone
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Firebase initialization
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "url"
})

# Load the encoding file
print("Loading Encode File...")
try:
    with open('EncodeFile.p', 'rb') as file:
        encodeListKnownWithIds = pickle.load(file)
except FileNotFoundError:
    print("EncodeFile.p is missing. Exiting...")
    exit()

encodeListKnown, studentIds = encodeListKnownWithIds
print("Encode File Loaded.")

# Setup for local video feed
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Width
cap.set(4, 480)  # Height

# Load static resources
if not os.path.exists('Resources/background.png'):
    print("background.png is missing. Exiting...")
    exit()
imgBackground = cv2.imread('Resources/background.png')

# Load mode images into a list
folderModePath = 'Resources/Modes'
if not os.path.exists(folderModePath):
    print(f"{folderModePath} is missing. Exiting...")
    exit()

modePathList = os.listdir(folderModePath)
imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList]

# Local image folder for student photos
folderStudentImages = 'Images'

# Initial settings
modeType = 0
counter = 0
id = -1
imgStudent = []
studentInfo = {}

# Helper Function to Center Text
def center_text(img, text, x_offset, y, font, scale, color, thickness):
    (w, _), _ = cv2.getTextSize(text, font, scale, thickness)
    x = x_offset + (414 - w) // 2
    cv2.putText(img, text, (x, y), font, scale, color, thickness)

# Main loop
while True:
    success, img = cap.read()
    if not success:
        print("Failed to capture frame. Exiting...")
        break

    # Resize and convert frame for face recognition
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # Detect faces and encode
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    # Place video feed and mode images on the background
    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurFrame:
        print(f"Detected {len(faceCurFrame)} faces.")
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            print(f"Face distances: {faceDis}")

            # Find the best match
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                id = studentIds[matchIndex]
                print(f"Detected ID: {id}")

                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

                if counter == 0:
                    counter = 1
                    modeType = 1

                # Fetch student data from the database
                studentInfo = db.reference(f'Students/{id}').get()

                if studentInfo is None:
                    print(f"No student info found for ID: {id}.")
                    continue

                print("Student Info:", studentInfo)

                # Fetch student image from local storage
                imgPath = os.path.join(folderStudentImages, f"{id}.png")
                print(f"Loading student image from: {imgPath}")
                imgStudent = cv2.imread(imgPath) if os.path.exists(imgPath) else np.zeros((216, 216, 3), dtype=np.uint8)

                # Check if the image loaded correctly
                if imgStudent is None or imgStudent.size == 0:
                    print(f"Error loading image for ID: {id}")
                    imgStudent = np.zeros((216, 216, 3), dtype=np.uint8)  # Blank image if not found
                else:
                    imgStudent = cv2.resize(imgStudent, (216, 216))  # Ensure the image is the correct size

                # Check and update attendance
                lastAttendanceTime = studentInfo.get('last_attendance_time', '1970-01-01 00:00:00')
                datetimeObject = datetime.strptime(lastAttendanceTime, "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()

                if secondsElapsed > 30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0

    if counter != 0 and studentInfo:
        if 10 < counter < 20:
            modeType = 2

        if counter <= 450:
            cv2.putText(imgBackground, str(studentInfo['total_attendance']), (880, 135),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
            cv2.putText(imgBackground, str(studentInfo['major']), (1000, 550),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(imgBackground, str(id), (1000, 495),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(imgBackground, str(studentInfo['standing']), (900, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
            cv2.putText(imgBackground, str(studentInfo['year']), (1020, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
            cv2.putText(imgBackground, str(studentInfo['starting_year']), (1130, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
            center_text(imgBackground, studentInfo['name'], 808, 445, cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)
            imgBackground[170:170 + 216, 930:930 + 216] = imgStudent

        counter += 1
        if counter >= 450:
            counter = 0
            modeType = 0
            studentInfo = {}
            imgStudent = []

    # Display the attendance system interface
    cv2.imshow("Face Attendance", imgBackground)
    key = cv2.waitKey(1)
    if key == ord('q'):  # Exit on 'q'
        break

cap.release()
cv2.destroyAllWindows()
