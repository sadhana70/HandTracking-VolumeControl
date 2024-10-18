import cv2
import mediapipe as mp
import osascript as osa
import numpy as np
import math


class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                       min_detection_confidence=float(self.detectionCon), 
            min_tracking_confidence=float(self.trackCon))
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):

        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                # print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                # print(id, cx, cy)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        return lmList


def process_frame(img, lmList):
    vol = 0
    barVol = 400
    minVol, maxVol = 0, 100
    finDiffMin, finDiffMax = 20, 200

    if lmList:
        # Thumb tip: 4, Index finger tip: 8
        thumbX, thumbY = lmList[4][1], lmList[4][2]
        indexX, indexY = lmList[8][1], lmList[8][2]
        midX, midY = (thumbX + indexX) // 2, (thumbY + indexY) // 2

        cv2.circle(img, (thumbX, thumbY), 10, (128, 0, 0), cv2.FILLED)
        cv2.circle(img, (indexX, indexY), 10, (128, 0, 0), cv2.FILLED)
        cv2.circle(img, (midX, midY), 5, (128, 0, 0), cv2.FILLED)
        cv2.line(img, (thumbX, thumbY), (indexX, indexY), (128, 0, 0), 2)

        # Calculate distance between thumb and index finger
        finDiff = math.hypot(indexX - thumbX, indexY - thumbY)

        # Adjust volume based on distance
        vol = np.interp(finDiff, [finDiffMin, finDiffMax], [minVol, maxVol])
        osa.run(f'set volume output volume {str(int(vol))}')

        # Update the visual volume bar
        barVol = np.interp(finDiff, [finDiffMin, finDiffMax], [400, 150])
        if finDiff < 30:
            cv2.circle(img, (midX, midY), 10, (255, 0, 0), cv2.FILLED)

    return img, vol, barVol