
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from db import init_db, insert_employee, get_all_employees, mark_attendance

from io import BytesIO
from PIL import Image
import base64
import os
from datetime import datetime
from src.anti_spoof_predict import AntiSpoofPredict
from src.generate_patches import CropImage
from src.utility import parse_model_name
import numpy as np
from deepface import DeepFace




app = Flask(__name__)
app.secret_key = "face_attendance_secret"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ------------------ Initialize Database ------------------
init_db()

@app.route('/')
def home():
    print("\U0001F3E0 Redirecting to register page...")
    return redirect(url_for('register'))

# ------------------ Register Employee ------------------
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        emp_id = request.form['emp_id']
        name = request.form['name']
        joining_date = request.form['joining_date']
        photo = request.files['photo']

        if emp_id and name and photo:
            img_path = os.path.join(UPLOAD_FOLDER, f"{emp_id}_photo.jpg")
            photo.save(img_path)
            print(f"\U0001F4F8 Photo saved for {emp_id} at {img_path}")

            with open(img_path, "rb") as f:
                insert_employee(emp_id, name, joining_date, f.read())
                print(f"Registered: {emp_id} - {name} on {joining_date}")

            flash("Employee registered successfully!")
            return redirect(url_for("register"))
        else:
            flash(" Please fill all fields and upload a photo.")
            print(" Missing registration data.")

    return render_template("register.html")


def get_greeting(hour):
    if 5 <= hour < 12: return "Good morning"
    if 12 <= hour < 17: return "Good afternoon"
    if 17 <= hour < 22: return "Good evening"
    return "Hello"

@app.route('/attendance', methods=["GET", "POST"])
def attendance():
    if request.method == "POST":
        image_data = request.form.get("image_data")
        punch_type = request.form.get("punch_type")  # IN or OUT

        if not image_data or not punch_type:
            flash("Missing image or punch type.|no_schedule")
            print("Missing image or punch_type from form.")
            return redirect(url_for("attendance"))

        try:
            # Decode base64 webcam image to numpy array
            header, encoded = image_data.split(",", 1)
            decoded = base64.b64decode(encoded)
            webcam_image = np.array(Image.open(BytesIO(decoded)).convert("RGB"))
        except Exception as e:
            flash(f"Failed to process image: {e}|no_schedule")
            print(f"Error decoding image: {e}")
            return redirect(url_for("attendance"))

        employees = get_all_employees()
        print(f"🧑‍💼 Loaded {len(employees)} employees from DB.")

        for emp_id, name, photo_blob in employees:
            try:
                db_image = np.array(Image.open(BytesIO(photo_blob)).convert("RGB"))

                result = DeepFace.verify(
                    webcam_image,
                    db_image,
                    model_name="Facenet",
                    enforce_detection=False
                )

                print(f"🔍 Comparing {emp_id}: Verified={result['verified']}, Distance={result['distance']}")

                if result["verified"]:
                    mark_attendance(emp_id, name, punch_type)
                    now = datetime.now()
                    greeting = get_greeting(now.hour)
                    timestamp = now.strftime("%d %B %Y, %I:%M:%S %p")
                    flash(f"{greeting} {name} ({emp_id})\n✅ Punch {punch_type} on {timestamp}")
                    print(f"✅ Attendance marked: {name} ({emp_id}) - {punch_type} at {timestamp}")
                    return redirect(url_for("attendance"))
            except Exception as e:
                print(f"🚫 DeepFace error for {emp_id}: {e}")

        flash("❌ No matching face found.")
        print("⚠️ No face matched.")
        return redirect(url_for("attendance"))

    print("📺 Opening attendance page...")
    return render_template("attendance.html")




@app.route("/detect_spoof", methods=["POST"])
def detect_spoof():
    MODEL_DIR = r"resources/anti_spoof_models"  # Use forward slashes (cross-platform)

    try:
        image_data = request.form.get("image_data")
        if not image_data:
            return jsonify({"status": "error", "message": "Missing image_data"})

        # Decode base64 image
        header, encoded = image_data.split(",", 1)
        decoded = base64.b64decode(encoded)
        img = Image.open(BytesIO(decoded)).convert("RGB")
        img_np = np.array(img)[:, :, ::-1]  # RGB to BGR

        model_test = AntiSpoofPredict(0)
        image_cropper = CropImage()
        image_bbox = model_test.get_bbox(img_np)

        if image_bbox is None:
            return jsonify({"status": "error", "message": "No face detected"})

        prediction = np.zeros((1, 3))

        for model_name in os.listdir(MODEL_DIR):
            model_path = os.path.join(MODEL_DIR, model_name)
            h_input, w_input, model_type, scale = parse_model_name(model_name)

            param = {
                "org_img": img_np,
                "bbox": image_bbox,
                "scale": scale,
                "out_w": w_input,
                "out_h": h_input,
                "crop": True,
            }
            if scale is None:
                param["crop"] = False

            cropped_img = image_cropper.crop(**param)
            prediction += model_test.predict(cropped_img, model_path)

        label = np.argmax(prediction)
        status = "real" if label == 1 else "fake"

        # Convert bbox from [x1, y1, x2, y2] to [x, y, width, height]
        x1, y1, x2, y2 = image_bbox
        x, y = int(x1), int(y1)
        w, h = int(x2 - x1), int(y2 - y1)

        return jsonify({
            "status": status,
            "bbox": [x, y, w, h]
        })

    except Exception as e:
        print("[ERROR] Spoof check failed:", e)
        return jsonify({"status": "error", "message": str(e)})
# ------------------ Run Server ------------------
if __name__ == "__main__":
    print("\U0001F680 Starting Face Attendance Server...")
    app.run(debug=True)
