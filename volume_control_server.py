import cv2
import numpy as np
import math
import module as ht
import osascript as osa
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (HTML, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize your hand tracking model
detector = ht.handDetector(detectionCon=0.7)

# Initialize video capture
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Capture frame-by-frame
            ret, img = cap.read()
            if not ret:
                break

            # Find hands
            img = detector.findHands(img)
            lmList = detector.findPosition(img)

            if lmList:
                # Your existing hand tracking logic here
                thumbX, thumbY = lmList[4][1], lmList[4][2]
                indexX, indexY = lmList[8][1], lmList[8][2]
                
                # Calculate distance
                finDiff = math.hypot(indexX-thumbX, indexY-thumbY)
                
                # Map to volume
                vol = np.interp(finDiff, [20, 200], [0, 100])
                vol = int(vol)

                # Set system volume
                osa.run(f'set volume output volume {vol}')

                # Send volume and hand position to client
                await websocket.send_json({
                    "volume": vol,
                    "thumbX": thumbX,
                    "thumbY": thumbY,
                    "indexX": indexX,
                    "indexY": indexY
                })

            # Convert frame to JPEG
            _, buffer = cv2.imencode('.jpg', img)
            await websocket.send_bytes(buffer.tobytes())

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)