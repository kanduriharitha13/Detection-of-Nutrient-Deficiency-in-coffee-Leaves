from fastapi import FastAPI, File, UploadFile, Body # Added Body
from fastapi.middleware.cors import CORSMiddleware
from translator_logic import translate_text
from model_loader import model_loader
from remedies import get_remedy
from detect.opencv_detect import detect_defects
from chatbot_logic import get_coffee_bot_response # NEW IMPORT

import base64
import numpy as np
import cv2
import io
import os
import uvicorn

# --------------------------------------------------
# APP SETUP
# --------------------------------------------------
app = FastAPI(title="Plant Nutrient Deficiency Detector")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# PATHS
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "plant_disease_model.pt")
CLASS_INDICES_PATH = os.path.join(BASE_DIR, "class_indices.json")

# --------------------------------------------------
# LOAD MODEL ON STARTUP
# --------------------------------------------------
@app.on_event("startup")
async def startup_event():
    try:
        model_loader.load_model(MODEL_PATH, CLASS_INDICES_PATH)
        print("✅ Classification model loaded successfully")
    except Exception as e:
        print(f"❌ Model load failed: {e}")

# --------------------------------------------------
# HOME
# --------------------------------------------------
@app.get("/")
def home():
    return {"message": "Plant Nutrient Deficiency Detector API is running"}

# --------------------------------------------------
# CHATBOT ENDPOINT (NEW)
# --------------------------------------------------
@app.post("/chat")
async def chat(payload: dict = Body(...)):
    user_message = payload.get("message", "")
    response = get_coffee_bot_response(user_message)
    return {"reply": response}

@app.post("/translate")
async def translate_endpoint(payload: dict = Body(...)):
    text_to_translate = payload.get("text", "")
    target_lang = payload.get("target_lang", "en")
    
    result = translate_text(text_to_translate, target_lang)
    return {"translated_text": result}
# --------------------------------------------------
# CLASSIFICATION
# --------------------------------------------------
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not model_loader.model:
        return {"error": "Model not loaded"}

    contents = await file.read()
    image_stream = io.BytesIO(contents)

    try:
        prediction = model_loader.predict(image_stream)
        predicted_class = prediction["class"]
        remedies = get_remedy(predicted_class)

        return {
            "deficiency": predicted_class,
            "organic_remedy": remedies
        }

    except Exception as e:
        return {"error": str(e)}

# --------------------------------------------------
# DEFECT REGION DETECTION (OpenCV)
# --------------------------------------------------
@app.post("/detect-areas")
async def detect_areas(file: UploadFile = File(...)):
    contents = await file.read()

    # Decode image safely
    np_img = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if image is None:
        return {"error": "Invalid image file"}

    original = image.copy()

    # Detect defect regions
    boxes = detect_defects(image)

    # Draw bounding boxes
    for (x1, y1, x2, y2) in boxes:
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 4)

    # Encode boxed image
    _, buf_boxed = cv2.imencode(".jpg", image)
    boxed_b64 = base64.b64encode(buf_boxed).decode("utf-8")

    # Encode original image (optional but useful)
    _, buf_orig = cv2.imencode(".jpg", original)
    orig_b64 = base64.b64encode(buf_orig).decode("utf-8")

    return {
        "total_defected_regions": len(boxes),
        "boxed_image": boxed_b64,
        "original_image": orig_b64,
        "boxes": boxes
    }

# --------------------------------------------------
# RUN SERVER
# --------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)