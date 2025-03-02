import cv2
import face_recognition
import pickle
import os
import logging
import firebase_admin
from firebase_admin import credentials, db

# Set up logging for error tracking
logging.basicConfig(filename='error_log.txt', level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Firebase
try:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': "https://faceattendancesystem-b34c4-default-rtdb.firebaseio.com/"
    })
    print("Firebase initialized successfully.")
except FileNotFoundError:
    logging.error("Firebase credential file not found.")
    print("Error: Firebase credential file 'serviceAccountKey.json' not found.")
    exit(1)
except Exception as e:
    logging.error(f"Firebase initialization failed: {e}")
    print(f"Error initializing Firebase: {e}")
    exit(1)

# Paths and data initialization
folderPath = 'Images'
if not os.path.exists(folderPath):
    print(f"Error: Folder '{folderPath}' not found.")
    logging.error(f"Folder '{folderPath}' not found.")
    exit(1)

studentIds = []
imgList = []

# Function to process and encode images
def processImages():
    global imgList, studentIds

    # Load file paths from the folder
    try:
        pathList = os.listdir(folderPath)
        print("Files in directory:", pathList)
    except Exception as e:
        print(f"Error reading folder '{folderPath}': {e}")
        logging.error(f"Error reading folder '{folderPath}': {e}")
        return

    # Filter and process image files
    imgList.clear()
    studentIds.clear()
    for path in pathList:
        if not path.startswith('.') and path.endswith(('.png', '.jpg', '.jpeg')):  # Only process image files
            filePath = os.path.join(folderPath, path)
            try:
                img = cv2.imread(filePath)
                if img is None:  # Skip invalid images
                    print(f"Error: Unable to load {path}. Skipping...")
                    logging.error(f"Unable to load {path}.")
                    continue
                # Resize images to reduce memory usage
                img = cv2.resize(img, (800, 800))
                imgList.append(img)
                studentIds.append(os.path.splitext(path)[0])  # Extract student ID from filename
            except Exception as e:
                print(f"Error processing image {path}: {e}")
                logging.error(f"Error processing image {path}: {e}")
                continue

    print("Unique Student IDs:", studentIds)

# Function to encode images
def findEncodings(imagesList):
    encodeList = []
    for idx, img in enumerate(imagesList):
        try:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB
            encode = face_recognition.face_encodings(img)
            if len(encode) > 0:  # Check if encoding is successful
                encodeList.append(encode[0])
            else:
                print(f"No face found in image {idx + 1}. Skipping...")
                logging.warning(f"No face found in image {idx + 1}.")
        except Exception as e:
            print(f"Error during encoding image {idx + 1}: {e}")
            logging.error(f"Error during encoding image {idx + 1}: {e}")
    return encodeList

# Function to save encodings to file
def saveEncodings():
    print("Encoding Started ...")
    try:
        if not imgList:
            print("No images to encode.")
            logging.warning("No images to encode.")
            return

        encodeListKnown = findEncodings(imgList)
        encodeListKnownWithIds = [encodeListKnown, studentIds]
        print("Encoding Complete")

        # Save encodings to a file
        with open("EncodeFile.p", 'wb') as file:
            pickle.dump(encodeListKnownWithIds, file)
        print("File Saved")
    except Exception as e:
        print(f"Error during encoding or saving: {e}")
        logging.error(f"Error during encoding or saving: {e}")

# Firebase listener for real-time updates
def dbListener(event):
    print("Database updated:", event.data)
    processImages()
    saveEncodings()

# Attach listener to the database
try:
    students_ref = db.reference('students')
    students_ref.listen(dbListener)
    print("Database listener attached.")
except Exception as e:
    print(f"Error attaching database listener: {e}")
    logging.error(f"Error attaching database listener: {e}")

# Initial processing
processImages()
saveEncodings()
