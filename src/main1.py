import cv2
import mediapipe as mp
import socket
import time

# 初始化 MediaPipe 手势检测
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands()

# TCP/IP 设置
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
        return "START"
    elif all_fingers_down(thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip, palm_base):
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

def all_fingers_down(thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip, palm_base):
    return (
        thumb_tip.y > palm_base.y and 
        index_tip.y > palm_base.y and 
        middle_tip.y > palm_base.y and 
        ring_tip.y > palm_base.y and 
        pinky_tip.y > palm_base.y
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

# 初始化变量用于存储手的位置信息
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
                            x_move = 1  # 沿X轴正方向移动
                            gesture += ",100,0,0"
                        elif current_x < previous_x:
                            x_move = -1  # 沿X轴负方向移动
                            gesture += ",-100,0,0"
                    elif gesture == "Y_MOVE":
                        if current_y > previous_y:
                            y_move = -1  # 沿Y轴负方向移动
                            gesture += ",0,-100,0"
                        elif current_y < previous_y:
                            y_move = 1  # 沿Y轴正方向移动
                            gesture += ",0,100,0"
                    elif gesture == "Z_MOVE":
                        if current_x > previous_x:
                            z_move = 1  # 沿Z轴正方向移动
                            gesture += ",0,0,100"
                        elif current_x < previous_x:
                            z_move = -1  # 沿Z轴负方向移动
                            gesture += ",0,0,-100"

                # 更新上一帧的手部位置
                previous_x = current_x
                previous_y = current_y

                # 将运动方向发送到服务器
                client_socket.send(gesture.encode())
                time.sleep(0.5)  # 增加延迟时间

                print(f"Detected Gesture: {gesture}")

    cv2.imshow('Hand Tracking', frame)
    
    # 按下 'q' 键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(1)  # 每次检测之间间隔1秒

cap.release()
client_socket.close()
cv2.destroyAllWindows()
