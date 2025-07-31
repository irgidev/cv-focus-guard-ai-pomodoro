# Focus Guard: AI-Powered Pomodoro Timer

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

An intelligent desktop Pomodoro timer that uses your webcam to detect loss of focus and helps you stay on track.

---

## About The Project

In today's world, maintaining focus is a significant challenge. Focus Guard is a smart productivity tool designed to combat distractions. It enhances the classic **Pomodoro Technique** by integrating a real-time, AI-powered focus detection module.

Using your webcam, Focus Guard monitors your head pose and eye state to determine if you are engaged with your task. If it detects that you're looking away, looking down, or showing signs of drowsiness, it provides a gentle alert, guiding you back to your work.

## Key Features

* **Configurable Pomodoro Timer:**
    * Set custom durations for Work, Short Break, and Long Break sessions.
    * Configure the number of work sessions before a long break.
* **AI-Powered Focus Detection:** (Active only during "Work" sessions)
    * **Head Pose Estimation:** Detects if you are looking away (yaw) or looking down (pitch) for an extended period.
    * **Drowsiness Detection:** Utilizes Eye Aspect Ratio (EAR) to identify if your eyes are closed for too long, differentiating blinks from genuine fatigue.
* **Tiered Alert System:**
    * A non-intrusive visual warning appears first.
    * An audible alarm sounds only if the lack of focus persists.
* **Simple & Clean UI:**
    * An intuitive interface built with CustomTkinter.
    * Includes an integrated webcam feed for visual feedback.

## Built With

This project leverages a powerful stack of modern Python libraries:

* [Python 3.9+](https://www.python.org/)
* [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
* [OpenCV](https://opencv.org/)
* [MediaPipe](https://mediapipe.dev/)
* [Pygame](https://www.pygame.org/news) (for audio playback)

---

## Getting Started

Follow these steps to get a local copy up and running.

### Prerequisites

Ensure you have Python 3.9 or newer installed on your system.
* [Python](https://www.python.org/downloads/)
* `pip` (Python's package installer)

### Installation

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/irgidev/cv-focus-guard-ai-pomodoro.git](https://github.com/irgidev/cv-focus-guard-ai-pomodoro.git)
    cd focus-guard-ai-pomodoro
    ```

2.  **Create and activate a virtual environment:**
    ```sh
    # Create the venv
    python -m venv venv

    # Activate it
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install the required packages:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Set up audio assets:**
    * Create a folder named `assets` in the project's root directory.
    * Place two audio files (`.mp3` or `.wav`) inside it:
        * `session_end.mp3`: Plays when a session is over.
        * `focus_alert.mp3`: Plays when focus is lost.
    * Ensure the filenames match those in `main.py` or update the paths in the script.

## Usage

To run the application, execute the `main.py` script from your terminal:

```sh
python main.py
```

---

## License

Distributed under the MIT License. See `LICENSE` for more information.