import uvicorn
import numpy as np
import tensorflow as tf
from io import BytesIO
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.preprocessing.image import load_img, img_to_array

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load TFLite model
interpreter = tf.lite.Interpreter(model_path="Tongue_Diabetes_Classifier.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

IMG_SIZE = (224, 224)

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    image = load_img(BytesIO(contents), target_size=IMG_SIZE)
    img = img_to_array(image) / 255.0
    img = np.expand_dims(img, axis=0)

    interpreter.set_tensor(input_details[0]['index'], img.astype(np.float32))
    interpreter.invoke()
    result = interpreter.get_tensor(output_details[0]['index'])[0][0]

    label = "Diabetic" if result > 0.5 else "Non-Diabetic"
    confidence = float(result if result > 0.5 else 1 - result)

    return {"prediction": label, "confidence": round(confidence, 2)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
