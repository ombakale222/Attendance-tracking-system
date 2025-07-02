import cv2
import numpy as np
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import onnxruntime as ort
import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from YOLO import YOLOv5

COLOR_REAL = (0, 255, 0)
COLOR_FAKE = (0, 0, 255)
COLOR_BOX = (0, 255, 255)

def increased_crop(img, bbox: tuple, bbox_inc: float = 1.5):
    real_h, real_w = img.shape[:2]
    x1, y1, x2, y2 = bbox
    w, h = x2 - x1, y2 - y1
    l = max(w, h)
    cx, cy = x1 + w // 2, y1 + h // 2

    new_l = int(l * bbox_inc)
    x_start = max(0, cx - new_l // 2)
    y_start = max(0, cy - new_l // 2)
    x_end = min(real_w, cx + new_l // 2)
    y_end = min(real_h, cy + new_l // 2)

    cropped = img[y_start:y_end, x_start:x_end]
    cropped = cv2.resize(cropped, (112, 112))  # ✅ model expects 112x112
    return cropped

class AntiSpoof:
    def __init__(self, model_path):
        self.session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
        self.input_name = self.session.get_inputs()[0].name
        print(f"[INFO] Loaded model: {model_path}")
        print(f"[INFO] Model input: {self.input_name}, shape: {self.session.get_inputs()[0].shape}")

    def __call__(self, input_tensor: np.ndarray):
        return self.session.run(None, {self.input_name: input_tensor})

class AntiSpoofApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Live Face Detection + Anti-Spoofing")

        self.face_detector = YOLOv5('face_attendance\yolov5s-face.onnx')
        self.anti_spoof = AntiSpoof('face_attendance\modelrgb.onnx')
        self.threshold = 0.1

        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Cannot access webcam.")
            exit()

        self.label = tk.Label(root)
        self.label.pack()

        self.capture_btn = tk.Button(root, text="Capture and Classify", command=self.classify_face)
        self.capture_btn.pack(pady=10)

        self.current_frame = None
        self.last_detected_bbox = None
        self.last_cropped_face = None

        self.update_frame()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame.copy()
            display_frame = frame.copy()

            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            bboxes = self.face_detector([img_rgb])[0]

            if bboxes.shape[0] > 0:
                bbox = bboxes[0][:4].astype(int)
                self.last_detected_bbox = bbox
                self.last_cropped_face = increased_crop(img_rgb, bbox)
                x1, y1, x2, y2 = bbox
                cv2.rectangle(display_frame, (x1, y1), (x2, y2), COLOR_BOX, 2)
                cv2.putText(display_frame, " ", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_BOX, 2)
            else:
                self.last_detected_bbox = None
                self.last_cropped_face = None

            img = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.configure(image=imgtk)

        self.root.after(10, self.update_frame)

    def classify_spoof_type_offline(self, face_img: np.ndarray) -> str:
        """
        Detects type of spoof: printed photo, mobile screen, video replay,
        including close-up mobile attacks.
        """
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness = np.mean(face_img)
        saturation = np.mean(cv2.cvtColor(face_img, cv2.COLOR_BGR2HSV)[:, :, 1])
        edge_density = np.sum(edges > 0) / (face_img.shape[0] * face_img.shape[1])
        h, w = face_img.shape[:2]
        aspect_ratio = w / h if h != 0 else 1

        # NEW: Full-face fill ratio detection (for mobile close spoof)
        face_area = np.count_nonzero(gray > 40)
        fill_ratio = face_area / (h * w)

        if fill_ratio > 0.95 and sharpness < 25:
            return "mobile_screen_close"
        elif brightness > 180 and sharpness > 30:
            return "printed_photo"
        elif edge_density > 0.01 and sharpness < 20:
            return "mobile_screen"
        elif 0.1 < aspect_ratio < 0.75:
            return "mobile_screen"
        elif sharpness < 5 or saturation > 140:
            return "video_replay"
        else:
            return None

    def classify_face(self):
        if self.last_detected_bbox is None or self.last_cropped_face is None:
            messagebox.showwarning("Classification", "No face detected.")
            return

        try:
            face = self.last_cropped_face.astype(np.float32) / 255.0
            face = np.transpose(face, (2, 0, 1))  # HWC -> CHW
            face = np.expand_dims(face, axis=0)  # (1, 3, 112, 112)

            result = self.anti_spoof(face)
            pred = result[0]
            score = float(pred[0][0])
            label = int(np.argmax(pred))

            frame = self.current_frame.copy()
            x1, y1, x2, y2 = self.last_detected_bbox

            if label == 0 and score >= self.threshold:
                spoof_type = self.classify_spoof_type_offline(self.last_cropped_face)
                if spoof_type:
                    label = 1
                    text = f"{spoof_type.upper()} FAKE"
                    color = COLOR_FAKE
                    messagebox.showwarning("Result", f"❌ FAKE ({spoof_type.upper()})")
                else:
                    text = f"REAL   {score:.2f}"
                    color = COLOR_REAL
                    messagebox.showinfo("Result", f"❌ FAKE FACE\nScore: {score:.2f}")
            else:
                text = f"FAKE   {score:.2f}"
                color = COLOR_FAKE
                messagebox.showwarning("Result", f"✅ REAL FACE\nScore: {score:.2f}")

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.configure(image=imgtk)

        except Exception as e:
            messagebox.showerror("Error", f"Prediction failed:\n{e}")
            print("Prediction error:", e)

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    root = tk.Tk()
    app = AntiSpoofApp(root)
    root.mainloop()
