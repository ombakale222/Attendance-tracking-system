import os
import cv2
import numpy as np
import time
import warnings

from src.anti_spoof_predict import AntiSpoofPredict
from src.generate_patches import CropImage
from src.utility import parse_model_name
warnings.filterwarnings('ignore')
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'code'))

MODEL_DIR = r"face_attendance\resources\anti_spoof_models"
DEVICE_ID = 0  # GPU device ID

def main():
    model_test = AntiSpoofPredict(DEVICE_ID)
    image_cropper = CropImage()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam")
        return

    print("[INFO] Starting real-time face anti-spoofing... Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to grab frame")
            break

        try:
            image_bbox = model_test.get_bbox(frame)
            prediction = np.zeros((1, 3))
            for model_name in os.listdir(MODEL_DIR):
                h_input, w_input, model_type, scale = parse_model_name(model_name)
                param = {
                    "org_img": frame,
                    "bbox": image_bbox,
                    "scale": scale,
                    "out_w": w_input,
                    "out_h": h_input,
                    "crop": True,
                }
                if scale is None:
                    param["crop"] = False

                img = image_cropper.crop(**param)
                prediction += model_test.predict(img, os.path.join(MODEL_DIR, model_name))

            label = np.argmax(prediction)
            value = prediction[0][label] / 2
            if label == 1:
                result_text = f" "
                color = (0, 255, 0)
            else:
                result_text = f"you are use image/video"
                color = (0, 0, 255)

            # Draw result
            cv2.rectangle(
                frame,
                (image_bbox[0], image_bbox[1]),
                (image_bbox[0] + image_bbox[2], image_bbox[1] + image_bbox[3]),
                color, 2
            )
            cv2.putText(
                frame,
                result_text,
                (image_bbox[0], image_bbox[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2
            )

        except Exception as e:
            print("[WARNING] No face detected or error:", e)

        # Show the result
        cv2.imshow("Real-Time Anti-Spoofing", frame)

        # Quit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Stopped.")


if __name__ == "__main__":
    main()
