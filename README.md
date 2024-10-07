# Gesture control robotic arm system

This project integrates computer vision, network communication, and robotic control to remotely control an ABB robotic arm through hand gestures. The system uses Python for gesture recognition and communication, while RAPID controls the robotic arm. The architecture is modular, allowing for future expansion to control other robotic arms and more complex gestures.

## Features
- **Gesture Recognition**: Real-time hand gesture detection using a camera.
- **Network Communication**: Control signals are transmitted to the ABB robotic arm via TCP/IP.
- **Robotic Control**: The robotic arm's motion is simulated in RobotStudio based on the detected gestures.

## System Architecture
The system consists of two main components:
1. **Python (main2.py)**: Responsible for gesture recognition and sending control commands.
2. **RAPID (RobotStudio)**: Responsible for receiving commands and controlling the robot's motion in the simulation.

## Prerequisites
- **Python** (>= 3.7) with the following libraries:
  - `opencv-python`
  - `mediapipe`
  - `socket`
- **ABB RobotStudio**
  - Ensure RobotStudio is installed with a virtual controller configured.
- **Robot Communication Setup**
  - The robotic arm is controlled via a local TCP/IP connection. Ensure that the robot and the Python application are connected to the same network.

## Installation

1. Clone this repository:
   ```bash
   git clone git@github.com:YourUsername/Gesture-Control-Robotic-Arm.git
   cd Gesture-Control-Robotic-Arm
   ```

2. Install the required Python libraries:
   ```bash
   pip install opencv-python mediapipe
   ```

3. Set up ABB RobotStudio with the project files provided in the `src/` directory. Ensure that the RAPID script is loaded and the TCP/IP communication is configured.

## How to Run

### Step 1: Run the Python Gesture Recognition Code

In your terminal, navigate to the project directory and execute the Python code:

```bash
python src/main2.py
```

This will start the camera input, and the system will begin detecting hand gestures.

### Step 2: Run the RobotStudio Simulation

Open **RobotStudio** and start the simulation. Ensure that the RAPID code is running and that it can receive TCP/IP commands from the Python script. The robotic arm will move based on the gestures you make in front of the camera.

## Supported Gestures and Commands

| Gesture        | Command           | Description                                 |
| -------------- | ----------------- | ------------------------------------------- |
| Thumb Left     | `X_MOVE1000`       | Move the robotic arm 10 units along the X-axis (positive) |
| Thumb Right    | `X_MOVE-1000`      | Move the robotic arm 10 units along the X-axis (negative) |
| Index Finger Left | `Y_MOVE0100`    | Move the robotic arm 10 units along the Y-axis (positive) |
| Index Finger Right | `Y_MOVE0-100`  | Move the robotic arm 10 units along the Y-axis (negative) |
| Pinky Left     | `Z_MOVE0010`       | Move the robotic arm 10 units along the Z-axis (positive) |
| Pinky Right    | `Z_MOVE00-10`      | Move the robotic arm 10 units along the Z-axis (negative) |
| Open Hand      | `STOP`             | Stop the robotic arm's current action       |

## Troubleshooting

- **Connection issues**: Ensure that both your Python script and RobotStudio are running on the same network and that the TCP/IP connection is configured correctly.
- **Gesture detection not accurate**: Make sure your camera has good lighting and a clear view of your hand. Adjust the threshold settings in `main2.py` if needed.

## Future Enhancements

- Add more complex gesture controls to increase the robot's functionality.
- Explore integration with VR for a more immersive experience.
