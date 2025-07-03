# Attendance-tracking-system
Attendance tracking system
+---------------------------------+
|      🎥 Webcam Feed (Live)     |
+---------------------------------+
              |
              v
+---------------------------------+
|🛡️ Run Silent-Face-Anti-Spoofing |
|            Model                |
+---------------+-----------------+
                |
+-------+-------+-------+
| ❌ FAKE Face  | ✅ REAL Face  |
|               |               |
v               v               v
+-------------+ +---------------+
|  Ignore /   | |Proceed to Next|
|   Alert     | |     Step      |
+-------------+ +-------+-------+
                        |
                        v
+---------------------------------+
|  📸 Capture Face Image          |
|      (captured_face.jpg)        |
+---------------------------------+
              |
              v
+---------------------------------+
|🗄️ Query SQLite DB for Stored   |
|         Face Images             |
|   (SELECT emp_id, name, photo_path) |
+---------------------------------+
              |
              v
+---------------------------------+
|🔁 Loop Over Stored Images &     |
|   Compare via DeepFace          |
|  (DeepFace.verify(...))         |
+---------------------------------+
              |
+-------------+-------------+
|    ❌ NO Match           | ✅ YES Match       |
|                          |                    |
v                          v                    v
+--------------------------+ +------------------+
|❌ No Match → Reject Access |🔎 Get emp_id & name |
|  "User not matched"      |    from DB        |
+--------------------------+ +--------+---------+
                                      |
                                      v
+---------------------------------+
|⏰ Determine Punch In/Out Status |
+---------------------+-----------+
                      |
+-----------+---------+-----------+
|  Punch In           | Punch Out           |
|                     |                     |
v                     v                     v
+---------------------+ +---------------------+
|📝 Mark Attendance:  | |📝 Mark Attendance:  |
|      Punch In       | |     Punch Out       |
+---------------------+ +----------+----------+
                      |            |
                      +------------+
                                 |
                                 v
+---------------------------------+
|🌞 Display Message:              |
| "Good morning/evening, {name}   |
|  (ID: {emp_id})!                |
|  Punch In/Out Recorded."        |
+---------------------------------+
## 📽 Demo Video

[Click to watch demo](Attendance_system.mp4)

## 📦 Quick Start
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
