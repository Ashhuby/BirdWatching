import cv2
import mediapipe as mp
import pygame
import numpy as np
import sys
from cv2_enumerate_cameras import enumerate_cameras


def run_diagnostic():
    print(f"--- SYSTEM DIAGNOSTIC (Python {sys.version.split()[0]}) ---")

    # 1. TEST: Pygame (Graphics & Window)
    try:
        pygame.init()
        screen = pygame.display.set_mode((400, 300))
        pygame.display.set_caption("Diagnostic Tool")
        print("[SUCCESS] Pygame initialized and window created.")
    except Exception as e:
        print(f"[FAILED] Pygame error: {e}")

    # 2. TEST: cv2-enumerate-cameras (Hardware Detection)
    target_idx = 0
    cams = list(enumerate_cameras())
    if not cams:
        print("[FAILED] No cameras detected by enumerator.")
    else:
        print(f"[SUCCESS] {len(cams)} camera(s) detected.")
        for c in cams:
            if "Camo" in c.name:
                target_idx = c.index
                print(f" -> Found Camo at Index: {target_idx}")

    # 3. TEST: OpenCV + MediaPipe (Camera + AI)
    cap = cv2.VideoCapture(target_idx)
    mp_face = mp.solutions.face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True
    )

    print("Testing Feed & AI (Press 'Q' on the popup window to finish)...")

    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < 5000:  # Test for 5 seconds
        success, frame = cap.read()
        if not success:
            print("[FAILED] Could not read frame from camera.")
            break

        # Flip and convert for MediaPipe
        rgb_frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        results = mp_face.process(rgb_frame)

        # Display feedback in the Pygame window
        screen.fill((30, 30, 30))
        msg = "AI TRACKING ACTIVE" if results.multi_face_landmarks else "WAITING FOR FACE..."
        color = (0, 255, 0) if results.multi_face_landmarks else (255, 255, 0)

        font = pygame.font.SysFont("Arial", 24)
        text = font.render(msg, True, color)
        screen.blit(text, (50, 130))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break

    print("[SUCCESS] MediaPipe processed frames successfully.")
    cap.release()
    pygame.quit()
    print("--- ALL LIBRARIES VERIFIED ---")


if __name__ == "__main__":
    run_diagnostic()