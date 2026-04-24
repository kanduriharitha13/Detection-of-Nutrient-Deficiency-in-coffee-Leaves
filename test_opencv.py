import cv2
from detect.opencv_detect import detect_defects
import base64

# ⚠️ Use RAW STRING or double backslashes
IMAGE_PATH = r"C:\Users\korat\Downloads\Leaf-Nutrient-Deficiency-main\Leaf-Nutrient-Deficiency-main\Dataset\boron-B\boron-B\B (1).jpg"

# 1️⃣ Read image as BYTES
with open(IMAGE_PATH, "rb") as f:
    image_bytes = f.read()

# 2️⃣ Run defect detection
result_base64 = detect_defects(image_bytes)

# 3️⃣ Convert base64 → image
decoded = base64.b64decode(result_base64)

with open("opencv_result.jpg", "wb") as f:
    f.write(decoded)

print("✅ Defected regions saved as opencv_result.jpg")

# 4️⃣ Show image (optional)
img = cv2.imread("opencv_result.jpg")
cv2.imshow("Defected Regions", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
