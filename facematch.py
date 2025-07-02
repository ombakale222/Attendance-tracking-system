
import io
import sqlite3
import numpy as np
from PIL import Image
from base64 import b64decode
from deepface import DeepFace

# Database filename
DB_NAME = "employee_data.db"


def read_image_from_base64(base64_str: str) -> np.ndarray:
    """
    Decode a base64-encoded image string into a NumPy array.

    Args:
        base64_str (str): Base64-encoded image data (usually from frontend).

    Returns:
        np.ndarray: Decoded image in NumPy format.
    """
    try:
        header, encoded = base64_str.split(",", 1)
        img_bytes = b64decode(encoded)
        return np.array(Image.open(io.BytesIO(img_bytes)))
    except Exception as e:
        raise ValueError(f"Failed to decode base64 image: {e}")


def fetch_employee_images() -> list:
    """
    Fetch all employee records (ID, name, photo blob) from the database.

    Returns:
        list: List of tuples (emp_id, name, photo_blob).
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT emp_id, name, photo FROM employees")
        data = cursor.fetchall()
        conn.close()
        return data
    except sqlite3.Error as e:
        raise RuntimeError(f"Database error: {e}")


def find_matching_employee(base64_image: str) -> dict:
    """
    Compare input base64 image with stored employee photos using DeepFace.

    Args:
        base64_image (str): Base64 image string (from webcam or upload).

    Returns:
        dict: Matching result with employee info if verified, else {"verified": False}.
    """
    try:
        # Decode uploaded image
        input_image = read_image_from_base64(base64_image)

        # Load all employee face images from DB
        employees = fetch_employee_images()

        # Compare against each stored photo
        for emp_id, name, photo_blob in employees:
            db_image = np.array(Image.open(io.BytesIO(photo_blob)))

            # Run face verification
            result = DeepFace.verify(
                input_image,
                db_image,
                model_name="Facenet",
                enforce_detection=False
            )

            if result.get("verified", False):
                print(f"✅ Match found: {emp_id} - {name}")
                return {
                    "emp_id": emp_id,
                    "name": name,
                    "verified": True,
                    "distance": result.get("distance", None)
                }

        print("❌ No match found.")
        return {"verified": False}

    except Exception as e:
        print(f"🚫 Error during verification: {e}")
        return {"verified": False}
