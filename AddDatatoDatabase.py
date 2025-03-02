import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Initialize Firebase with the service account key and database URL
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancesystem-b34c4-default-rtdb.firebaseio.com/"
})

# Reference to the Students node in the database
ref = db.reference('Students')

# Corrected student data
data = {
    "23391181": {
        "name": "Vivek Mehra",
        "major": "Computer Application",
        "starting_year": 2023,
        "total_attendance": 0,
        "standing": "A",
        "year": 2,
        "last_attendance_time": "2024-11-20 00:54:34"
    },
    "23391194": {
        "name": "Vivek Saxena",
        "major": "Computer Application",
        "starting_year": 2023,
        "total_attendance": 0,
        "standing": "A",
        "year": 2,
        "last_attendance_time": "2024-11-19 00:54:34"
    },
    "23391361": {
        "name": "Nishant Singh Rawal",
        "major": "Computer Application",
        "starting_year": 2023,
        "total_attendance": 0,
        "standing": "C",
        "year": 2,
        "last_attendance_time": "2024-11-15 00:54:34"
    },
    "23391350": {
        "name": "Harshit Chaurasia",
        "major": "Computer Application",
        "starting_year": 2023,
        "total_attendance": 0,
        "standing": "C",
        "year": 2,
        "last_attendance_time": "2024-11-05 00:54:34"
    },
     "230313024": {
        "name": "Manish Mehra",
        "major": "Digital Marketing",
        "starting_year": 2023,
        "total_attendance": 0,
        "standing": "A",
        "year": 2,
        "last_attendance_time": "2024-11-25 00:54:34"
    },
      "23391195": {
        "name": "Nitin Joshi",
        "major": "Computer Application",
        "starting_year": 2023,
        "total_attendance": 0,
        "standing": "A",
        "year": 2,
        "last_attendance_time": "2024-11-25 00:54:34"
    },
      "237122494": {
        "name": "Divya",
        "major": "Computer Application",
        "starting_year": 2023,
        "total_attendance": 0,
        "standing": "E",
        "year": 2,
        "last_attendance_time": "2024-11-25 00:54:34"
    }
}

try:
    # Upload all data to the Students node
    ref.update(data)
    print("Data uploaded successfully.")
except Exception as e:
    print(f"Error uploading data: {e}")
