import cv2
import mediapipe as mp
import torch
import torch.nn.functional as F
from HandNetwork import HandNetwork
import time
from gestures import *

class Camera():

    def __init__(self, confidence_threshold=0.95):
        """
        Initializes the camera by setting up the model, capture session, frame counters, and confidence threshold
        """
        self.classes = ('A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','Space')
        self.model = HandNetwork(classes=self.classes)
        self.model = torch.load("models/model.pth")
        self.capture_session = cv2.VideoCapture(0)
        self.frame_counter = 0
        self.patience = 0
        self.low_power = 3 # this variable is for the fact that when a hand is not detected, it will only check if a hand is there every 3 frames, since the .process() method is expensive
        self.confidence_threshold = confidence_threshold

    def start_capture_session(self):
        """
        Starts up the camera and runs it, while periodically predicting the gesture in the camera's frame and calling the gesture functions.
        Also downscales itself when hand is not detected, and upscales when hand is detected, to preserve as much batter as possible.
        """
        mp_hands = mp.solutions.hands
        prev_time = 0
        default_width =  int(self.capture_session.get(3))
        default_height = int(self.capture_session.get(4))
        # we want to start of with a lower resolution (but scale it back up when a hand goes into frame)
        self.capture_session.set(cv2.CAP_PROP_FRAME_WIDTH, int(default_width/3)) 
        self.capture_session.set(cv2.CAP_PROP_FRAME_HEIGHT, int(default_height/3))
        with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5, max_num_hands=2) as hands:
            while self.capture_session.isOpened():
                ret, image = self.capture_session.read()
                self.frame_counter += 1
                landmarks = []
                if self.frame_counter % self.low_power == 0:
                    # Detections
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # changes from bgr to rgb since cv2 is bgr but mediapipe requires rgb
                    image.flags.writeable = False # we change writeable from true to false back to true again to optimize code
                    results = hands.process(image) # this makes the actual detections
                    image.flags.writeable = True
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                    if self.frame_counter % 3 == 0: # the 3 here means that in every 3 frames, it will look at the hand and predict its gesture
                        if results.multi_hand_landmarks:
                            self.capture_session.set(cv2.CAP_PROP_FRAME_WIDTH, default_width) # scale the input back up since its detecting hands
                            self.capture_session.set(cv2.CAP_PROP_FRAME_HEIGHT, default_height)
                            self.low_power = 1 # now that we know a hand is there, we want it to detect the hand every single frame until the hand goes away
                            for landmark in results.multi_hand_landmarks[0].landmark:
                                x, y = landmark.x, landmark.y
                                landmarks.append([x,y])
                            with torch.no_grad(): # we use torch.no_grad since during predictions we don't need to calculate gradients
                                landmarks = torch.tensor(landmarks)
                                out = self.model(landmarks.view(-1,21,2))
                                confidence = torch.max(F.softmax(out,1)).item() # softmax squishes values between 0 and 1, giving us confidence values to use
                                prediction = torch.argmax(out) # argmaxing this will give us our prediciton index
                                print(self.classes[prediction], confidence)
                                if confidence >= self.confidence_threshold: # if confidence is higher than the threshold, allow gesture commands to be used
                                    type_char(self.classes[prediction])

                        else: # if hand is not detected for a set amount of frames, downscale to save pwr
                            self.patience += 1
                            if self.patience%15 == 0:
                                self.capture_session.set(cv2.CAP_PROP_FRAME_WIDTH, int(default_width/3))
                                self.capture_session.set(cv2.CAP_PROP_FRAME_HEIGHT, int(default_height/3))
                                self.patience = 0
                                self.low_power = 3

                # Print fps
                curr_time = time.time()
                fps = 1 / (curr_time-prev_time)
                prev_time = curr_time
                image = cv2.flip(image,1)
                cv2.putText(image, f"FPS: {fps}", (20,70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 196, 255), 2)

                cv2.imshow("Hand Tracking", image)
                if cv2.waitKey(10) & 0xFF == ord('q'): # when 'q' is pressed, exit out of the camera
                    self.end_capture_session()
                    break
            
    def end_capture_session(self):
        """
        Stops the camera from reading any more input, and deletes the windows the video output was going to.
        """
        self.capture_session.release()
        cv2.destroyAllWindows()
