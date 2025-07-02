# from deepface import DeepFace

# def save_image(uploaded_file, path):
#     """Save uploaded image file to a specified path."""
#     with open(path, "wb") as f:
#         f.write(uploaded_file.read())


# def verify_face(img1_path, img2_path):
#     try:
#         print(f"🧪 Comparing:\n  📷 {img1_path}\n  📷 {img2_path}")
#         result = DeepFace.verify(img1_path, img2_path, model_name="Facenet", enforce_detection=False)
#         print("🔁 DeepFace Result:", result)
#         return result["verified"]
#     except Exception as e:
#         print(f"🚫 DeepFace verification error: {e}")
#         return False

from deepface import DeepFace


def save_image(uploaded_file, path: str):
    """
    Save an uploaded image file to the specified path.

    Args:
        uploaded_file (FileStorage): File-like object (e.g., from Flask `request.files`).
        path (str): Destination file path to save the image.
    """
    try:
        with open(path, "wb") as f:
            f.write(uploaded_file.read())
        print(f"💾 Image saved to: {path}")
    except Exception as e:
        print(f"🚫 Error saving image: {e}")


def verify_face(img1_path: str, img2_path: str) -> bool:
    """
    Compare two face images using DeepFace's verification model.

    Args:
        img1_path (str): Path to the first image (e.g., uploaded photo).
        img2_path (str): Path to the second image (e.g., stored employee photo).

    Returns:
        bool: True if a match is found, False otherwise.
    """
    try:
        print(f"🧪 Comparing faces:\n  📷 {img1_path}\n  📷 {img2_path}")

        # Perform face verification using Facenet
        result = DeepFace.verify(
            img1_path,
            img2_path,
            model_name="Facenet",
            enforce_detection=False  # Allow images without perfect face detection
        )

        print("✅ DeepFace Result:", result)
        return result.get("verified", False)

    except Exception as e:
        print(f"🚫 DeepFace verification error: {e}")
        return False
