# Attendance System

## 🌟 Overview

This project delivers a robust and secure attendance management system leveraging advanced computer vision and deep learning techniques. Its core innovation lies in its **real-time anti-spoofing capabilities**, ensuring that attendance is only marked for genuine, live individuals, effectively preventing fraudulent clock-ins using photos, videos, or masks. By integrating state-of-the-art anti-spoofing with reliable face recognition, this system provides an accurate and trustworthy solution for automated attendance.

## 🎯 Objective

The primary objective of this system is to build a secure attendance solution that **strictly marks attendance only if a real, live face is detected**. A critical function is its ability to **prevent attendance marking if a user attempts to spoof the system** using a mobile photo, printed image, or video. This ensures the integrity and accuracy of attendance records.

## ✨ Features

* **Real-time Anti-Spoofing:** Utilizes a `Silent-Face-Anti-Spoofing` model to differentiate between live faces and spoofing attempts.
* **Accurate Face Recognition:** Employs `DeepFace` for high-precision identity verification against a database of registered employees.
* **Secure Attendance Logging:** Records "Punch In" and "Punch Out" entries securely in a SQLite database.
* **Automated Workflow:** Streamlines the attendance process from face detection to record-keeping.
* **Personalized Feedback:** Provides instant on-screen confirmation with employee details and punch status.

## 🛠️ Technologies Used

The system integrates several key technologies and libraries:

* **Anti-Spoofing Model:**
    * `Silent-Face-Anti-Spoofing` 
* **Face Recognition & Analysis:**
    * `DeepFace` (Python library for face verification, recognition, and attribute analysis)
* **Database Management:**
    * `SQLite` (Lightweight, file-based database for storing employee photos and attendance logs)
    * `sqlite3` (Python standard library for SQLite interaction)
* **Webcam Interaction & Image Processing:**
    * `OpenCV` (`cv2` Python library)
* **User Interface (Optional):**
    * `Flask` (Python web framework for a browser-based interface, if applicable)
* **Core Language:**
    * `Python 3.12`

## 🚀 Getting Started

Follow these instructions to set up and run the project locally.

### Prerequisites

* Python 3.8+
* `pip` (Python package installer)
* A webcam connected to your system.

### Installation

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/your-repo/face-attendance-system.git](https://github.com/your-repo/face-attendance-system.git)
    cd face-attendance-system
    ```
2.  **Create and Activate Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    # For Windows:
    venv\Scripts\activate
    # For macOS/Linux:
    source venv/bin/activate
    ```
3.  **Upgrade pip & Install Requirements:**
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

### Database Setup

* Ensure you have an `employee.db` SQLite database in your project root (or configured path).
* This database should contain a table (e.g., `employees`) with `emp_id`, `name`, and `photo_path` columns.
* Pre-register employee faces by storing their images in a designated folder (e.g., `employee_photos/`) and populate the `employee.db` with corresponding `emp_id`, `name`, and `photo_path` entries.

### Running the System

1.  **Start the application:**
    ```bash
    python app.py
    ```
   

2.  **Access the system:**
    * If using a console-based interface, observe the output in your terminal.
    * If using Flask, open your web browser and navigate to `http://127.0.0.1:5000` (or the configured address).

## 💡 System Workflow (Detailed Steps)

The system operates through a precise, sequential workflow designed to prioritize anti-spoofing before proceeding to identity verification and attendance logging:

1.  **Real-Time Face Tracking & Anti-Spoofing Check**
    * The system continuously captures a live video feed from a webcam.
    * It actively tracks any faces detected within the video stream.
    * Crucially, for each detected face, the **`Silent-Face-Anti-Spoofing` model** is immediately applied. This model analyzes the face to determine its "liveness."
    * **Decision Point:**
        * **If the face is identified as FAKE (spoof attempt):** The system **blocks** attendance marking. It might display an alert ("FAKE Face Detected!") and simply continues monitoring the webcam, ignoring the spoof.
        * **If the face is identified as REAL (genuine person):** The system confirms the liveness of the face and proceeds to the next stage for identity verification.

2.  **Capture Live Face Image for Verification**
    * Once a face is confirmed as "REAL" by the anti-spoofing model, a high-quality still image of this live face is captured from the webcam feed.
    * This image is saved temporarily (e.g., as `captured_face.jpg`).

3.  **Query Stored Employee Photos**
    * The system connects to the `employee.db` SQLite database.
    * It retrieves a list of all registered employees, specifically fetching their `emp_id`, `name`, and the `photo_path` (the location of their pre-stored face image).

4.  **Face Recognition and Identity Verification**
    * The **`DeepFace` library** is used to perform identity verification.
    * The system iteratively compares the `captured_face.jpg` (the live, real face) against each of the stored employee photos retrieved from the database.
    * **Decision Point:**
        * **If NO Match is Found:** If the captured face does not match any of the registered employee photos, access is denied, and a message like "User not matched" is displayed. The attendance is **not** marked.
        * **If YES Match is Found:** If a match is successfully verified by DeepFace, the `emp_id` and `name` of the recognized employee are retrieved from the database.

5.  **Determine Punch Status & Mark Attendance**
    * Upon successful identity verification, the system checks the employee's existing attendance records for the current day to determine the appropriate action (e.g., if no entry exists, it's a "Punch In"; if a "Punch In" exists, it's a "Punch Out").
    * The attendance record (including `emp_id`, `name`, timestamp, and "Punch In" or "Punch Out" status) is then securely stored in the SQLite `attendance` table (or exported to CSV/Excel).

6.  **Display Confirmation Message**
    * A clear, personalized message is displayed to the employee, confirming their attendance action. Examples include: "Good morning, {name} (ID: {emp_id})! Punch In Recorded." or "Good evening, {name} (ID: {emp_id})! Punch Out Recorded."


