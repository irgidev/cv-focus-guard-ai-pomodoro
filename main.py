import customtkinter as ctk
import threading
import time
import pygame
import cv2
import mediapipe as mp
from PIL import Image
from focus_detector import FocusDetector

WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 20
SESSIONS_BEFORE_LONG_BREAK = 4

SOUND_SESSION_END = "assets/session_end.mp3" 
SOUND_FOCUS_ALERT = "assets/focus_alert.mp3"

COLOR_TEXT = "#FFFFFF"
COLOR_WARN = "#FFCC00"

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Focus Guard")
        self.root.geometry("400x650") 
        self.root.resizable(False, False)

        self.sessions = 0
        self.is_running = False
        self.is_paused = False
        self.current_time = WORK_MIN * 60
        self.current_session_type = "Work"
        self.timer_thread = None

        pygame.mixer.init()
        self.cap = cv2.VideoCapture(0)
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.drawing_spec = self.mp_drawing.DrawingSpec(thickness=1, circle_radius=1, color=(0, 255, 0))
        
        self.unfocused_counter = 0
        self.VISUAL_WARNING_THRESHOLD_FRAMES = 15 
        self.SOUND_ALERT_THRESHOLD_FRAMES = 45

        self.session_label = ctk.CTkLabel(root, text="", font=("Helvetica", 24, "bold"))
        self.session_label.pack(pady=10)

        self.timer_label = ctk.CTkLabel(root, text="", font=("Helvetica", 80, "bold"))
        self.timer_label.pack(pady=10)
        
        self.unfocused_reason_label = ctk.CTkLabel(root, text="", font=("Helvetica", 16), text_color=COLOR_WARN)
        self.unfocused_reason_label.pack(pady=5)

        control_frame = ctk.CTkFrame(root, fg_color="transparent")
        control_frame.pack(pady=10)
        
        self.start_button = ctk.CTkButton(control_frame, text="Start", command=self.start_timer, width=100)
        self.start_button.pack(side="left", padx=5)

        self.pause_button = ctk.CTkButton(control_frame, text="Pause", command=self.pause_timer, width=100, state="disabled")
        self.pause_button.pack(side="left", padx=5)

        self.reset_button = ctk.CTkButton(control_frame, text="Reset", command=self.reset_timer, width=100)
        self.reset_button.pack(side="left", padx=5)
        
        self.webcam_label = ctk.CTkLabel(root, text="")
        self.webcam_label.pack(pady=10)

        self.update_display()
        self.update_webcam()

    def play_sound(self, sound_file):
        try:
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play()
        except pygame.error as e:
            print(f"Tidak dapat memutar suara: {e}. Pastikan path file benar dan ada folder 'assets'.")

    def update_display(self):
        mins, secs = divmod(self.current_time, 60)
        self.timer_label.configure(text=f"{mins:02d}:{secs:02d}")
        self.session_label.configure(text=f"{self.current_session_type} Session ({self.sessions}/{SESSIONS_BEFORE_LONG_BREAK})")

    def countdown(self):
        while self.is_running and self.current_time > 0:
            if not self.is_paused:
                self.current_time -= 1
                self.root.after(0, self.update_display)
                time.sleep(1)
        
        if self.is_running and self.current_time == 0:
            self.play_sound(SOUND_SESSION_END)
            self.root.after(0, self.next_session)

    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.start_button.configure(state="disabled")
            self.pause_button.configure(state="normal")
            self.timer_thread = threading.Thread(target=self.countdown, daemon=True)
            self.timer_thread.start()

    def pause_timer(self):
        self.is_paused = not self.is_paused
        self.pause_button.configure(text="Resume" if self.is_paused else "Pause")

    def reset_timer(self):
        self.is_running = False
        self.is_paused = False
        self.sessions = 0
        self.current_session_type = "Work"
        self.current_time = WORK_MIN * 60
        self.update_display()
        self.start_button.configure(state="normal")
        self.pause_button.configure(state="disabled", text="Pause")
        self.unfocused_reason_label.configure(text="")

    def next_session(self):
        if self.current_session_type == "Work":
            self.sessions += 1
            if self.sessions % SESSIONS_BEFORE_LONG_BREAK == 0:
                self.current_session_type = "Long Break"
                self.current_time = LONG_BREAK_MIN * 60
            else:
                self.current_session_type = "Short Break"
                self.current_time = SHORT_BREAK_MIN * 60
        else:
            self.current_session_type = "Work"
            self.current_time = WORK_MIN * 60
        
        self.is_paused = False
        self.update_display()
        
        self.timer_thread = threading.Thread(target=self.countdown, daemon=True)
        self.timer_thread.start()

    def update_webcam(self):
        ret, frame = self.cap.read()
        if not ret:
            self.root.after(10, self.update_webcam)
            return

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)
        
        is_focus_module_active = (self.current_session_type == "Work" and self.is_running and not self.is_paused)

        if results.multi_face_landmarks and is_focus_module_active:
            for face_landmarks in results.multi_face_landmarks:
                self.mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.drawing_spec
                )
            
            detector = FocusDetector(results.multi_face_landmarks[0].landmark)
            unfocused_reason = detector.is_unfocused()

            if unfocused_reason:
                self.unfocused_counter += 1

                if self.unfocused_counter > self.VISUAL_WARNING_THRESHOLD_FRAMES:
                    self.unfocused_reason_label.configure(text=f"Peringatan: {unfocused_reason}")

                if self.unfocused_counter > self.SOUND_ALERT_THRESHOLD_FRAMES:
                    self.play_sound(SOUND_FOCUS_ALERT)
                    self.unfocused_counter = 0
            else:
                self.unfocused_counter = 0
                self.unfocused_reason_label.configure(text="")
        else:
            self.unfocused_counter = 0
            self.unfocused_reason_label.configure(text="")

        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(360, 270))
        self.webcam_label.configure(image=ctk_img)
        
        self.root.after(10, self.update_webcam)

    def on_closing(self):
        print("Menutup aplikasi...")
        self.is_running = False
        self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    app = PomodoroTimer(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
