# Attendance-tracking-system
# @ Wrorking 
1. # Live Video Feed & Face Tracking:
     The system continuously captures video from a webcam and actively tracks faces detected in the live stream.

2. # Real-Time Anti-Spoofing Check:
     For each detected face, a Silent-Face-Anti-Spoofing model analyzes it to determine if it's a live, genuine person or a spoofing attempt (e.g., photo, video, mask).

      # If FAKE Face:
             The system immediately rejects access, and an alert can be triggered or displayed. It then continues monitoring for new faces.

      # If REAL Face:
             The system validates the face as live and proceeds to the next step.

3. # Capture Live Face Image:
     A still image (captured_face.jpg) of the verified "REAL" face is captured and saved for identity verification.

5. # Query Employee Database:
     The system connects to a SQLite database and queries it to retrieve a list of all registered employees, including their emp_id, name, and the file path (photo_path) to their pre-stored   reference face            images.

6. # Face Recognition via DeepFace:
     The system then iterates through each registered employee's photo from the database.

     It uses the DeepFace library to compare the captured_face.jpg (the live photo) against each photo_path from the database.

     # If NO Match:
             If no match is found after comparing with all stored photos, access is rejected, and a "User not matched" message is displayed.

     # If YES Match:
             If a match is verified, the emp_id and name of the recognized employee are retrieved.

7. # Determine Punch Status:
     Based on the current time and the employee's existing attendance records for the day, the system determines if the current action should be a "Punch In" (e.g., first record of the day,     or last record was      a "Punch Out") or a "Punch Out" (e.g., already "Punched In").

8. # Mark Attendance Record:
     The attendance (either "Punch In" or "Punch Out") is recorded in the SQLite attendance database (or a CSV/Excel file), including the emp_id, name, and a timestamp.

9. # Display Confirmation Message:
     A personalized confirmation message is displayed to the employee, such as: "Good morning/evening, {name} (ID: {emp_id})! Punch In/Out Recorded."

## 📽 Demo Video

[Click to watch demo](Attendance_system.mp4)

## 📦Download / Installation 
Clone the Repository & Setup

git clone https://github.com/your-repo/face-attendance-system.git

cd face-attendance-system

Create virtual environment

python -m venv venv

venv\Scripts\activate   # Windows

source venv/bin/activate  # Linux/Mac

Upgrade pip & install requirements

pip install --upgrade pip

pip install -r requirements.txt

# Run the app
python app.py
