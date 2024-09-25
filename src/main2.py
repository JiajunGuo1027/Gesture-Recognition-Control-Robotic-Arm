import cv2
import mediapipe as mp
import socket
import time

# Initialize MediaPipe gesture detection
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands()

# TCP/IP setup
SERVER_IP = '127.0.0.1'
SERVER_PORT = 5000
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

cap = cv2.VideoCapture(0)

def detect_gesture(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    palm_base = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

    if all_fingers_up(thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip, palm_base):
        return "STOP"
    elif is_thumb_up_only(thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip, palm_base):
        return "X_MOVE"
    elif is_index_up_only(index_tip, thumb_tip, middle_tip, ring_tip, pinky_tip, palm_base):
        return "Y_MOVE"
    elif is_pinky_up_only(pinky_tip, thumb_tip, index_tip, middle_tip, ring_tip, palm_base):
        return "Z_MOVE"
    return None

def all_fingers_up(thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip, palm_base):
    return (
        thumb_tip.y < palm_base.y and 
        index_tip.y < palm_base.y and 
        middle_tip.y < palm_base.y and 
        ring_tip.y < palm_base.y and 
        pinky_tip.y < palm_base.y
    )

def is_thumb_up_only(thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip, palm_base):
    return (
        thumb_tip.y < palm_base.y and
        index_tip.y > palm_base.y and
        middle_tip.y > palm_base.y and
        ring_tip.y > palm_base.y and
        pinky_tip.y > palm_base.y
    )

def is_index_up_only(index_tip, thumb_tip, middle_tip, ring_tip, pinky_tip, palm_base):
    return (
        thumb_tip.y > palm_base.y and
        index_tip.y < palm_base.y and
        middle_tip.y > palm_base.y and
        ring_tip.y > palm_base.y and
        pinky_tip.y > palm_base.y
    )

def is_pinky_up_only(pinky_tip, thumb_tip, index_tip, middle_tip, ring_tip, palm_base):
    return (
        thumb_tip.y > palm_base.y and
        index_tip.y > palm_base.y and
        middle_tip.y > palm_base.y and
        ring_tip.y > palm_base.y and
        pinky_tip.y < palm_base.y
    )

# The initialization variable is used to store the hand position information
previous_x = None
previous_y = None

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = hands.process(image)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            gesture = detect_gesture(hand_landmarks)
            
            if gesture:
                x_move, y_move, z_move = 0, 0, 0
                current_x = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x
                current_y = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y

                if previous_x is not None and previous_y is not None:
                    if gesture == "X_MOVE":
                        if current_x > previous_x:
                            gesture += ",10,0,0"
                        elif current_x < previous_x:
                            gesture += ",-10,0,0"
                    elif gesture == "Y_MOVE":
                        if current_y > previous_y:
                            gesture += ",0,-10,0"
                        elif current_y < previous_y:
                            gesture += ",0,10,0"
                    elif gesture == "Z_MOVE":
                        if current_x > previous_x:
                            gesture += ",0,0,10"
                        elif current_x < previous_x:
                            gesture += ",0,0,-10"
                else:
                    if gesture == "STOP":
                        client_socket.send(gesture.encode())

                # Update the hand position in the previous frame
                previous_x = current_x
                previous_y = current_y

                # The direction of motion is sent to the server
                client_socket.send(gesture.encode())
                #time.sleep(0.2)  # Reduce latency

                print(f"Detected Gesture: {gesture}")

    cv2.imshow('Hand Tracking', frame)
    
    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(0.5)  # A smaller interval between each detection

cap.release()
client_socket.close()
cv2.destroyAllWindows()
