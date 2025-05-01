import os
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from emotion_recognition import EmotionRecognizer  # Ensure this is correctly imported

app = FastAPI()

# Ensure 'uploads' directory exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize the emotion recognizer
rec = EmotionRecognizer(emotions=["angry", "neutral", "sad"], balance=False, verbose=1, custom_db=False)

@app.get("/")
def home():
    return {"message": "Welcome to the Emotion Recognition API"}

@app.post("/predict")
async def predict_emotion(audio: UploadFile = File(...)):
    if not audio.filename:
        raise HTTPException(status_code=400, detail="No file selected")
    
    file_path = os.path.join(UPLOAD_FOLDER, audio.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(await audio.read())
        
        print(f"[INFO] Processing file: {file_path}")  # Debugging line
        prediction = rec.predict(file_path)  # Predict emotion
        accuracy = rec.test_score() * 100  # Convert to percentage
        print(f"[INFO] Prediction: {prediction}, Accuracy: {accuracy:.2f}%")  # Debugging line
        
        return JSONResponse(content={"emotion": prediction, "accuracy": f"{accuracy:.2f}%"})
    except Exception as e:
        print(f"[ERROR] {str(e)}")  # Print error message
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)     
