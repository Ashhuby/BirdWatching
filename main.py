import os
import cv2
from cv2_enumerate_cameras import enumerate_cameras
import numpy as np
import pygame
import mediapipe as mp
from mediapipe.python.solutions import face_mesh as mp_face_mesh
import time
from sprites import Bird

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


# --- 1. CONSOLE SOURCE SELECTION ---
def select_camera_source():
    print("\n" + "=" * 50)
    print("      SELECT VIDEO SOURCE")
    print("=" * 50)
    cameras = list(enumerate_cameras())
    for i, cam in enumerate(cameras):
        print(f"[{i}] {cam.name} {cam.index}")

    file_option = len(cameras)
    print(f"[{file_option}] blink.mp4 (TESTING MEDIAPIPE)")
    print(" 700 is fast loading && driver 1400 is higher resolution")
    print("=" * 50)

    choice = input(f"Select source index (0-{file_option}): ")
    try:
        idx = int(choice)
        if idx < len(cameras):
            return cameras[idx].index, True
        elif idx == len(cameras):
            return "blink.mp4", False
    except:
        pass
    return 0, True


selected_source, is_live = select_camera_source()

# --- COLORS ---
C_DEBUG, C_GRAPH, C_IRIS, C_EYE = (255, 50, 50), (0, 255, 255), (255, 255, 0), (255, 100, 255)

# --- LANDMARK INDICES ---
# Refined indices for eyelids and iris tracking
EYELID_INDICES = [33, 160, 158, 133, 153, 144, 362, 385, 387, 263, 373, 380,
                  7, 163, 161, 159, 157, 154, 155, 388, 386, 384, 390, 374, 382, 398]
IRIS_INDICES = [468, 469, 470, 471, 472, 473, 474, 475, 476, 477]


# --- UTILITIES ---
def load_asset(filename, size=None):
    path = os.path.join("assets", filename)
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        if size: img = pygame.transform.scale(img, size)
        return img
    return None

def get_ear(landmarks, w, h):
    idx = [33, 160, 158, 133, 153, 144]
    p = [np.array([landmarks.landmark[i].x * w, landmarks.landmark[i].y * h]) for i in idx]
    v1, v2 = np.linalg.norm(p[1] - p[5]), np.linalg.norm(p[2] - p[4])
    hor = np.linalg.norm(p[0] - p[3])
    return (v1 + v2) / (2.0 * hor)


# --- INITIALISE ---
pygame.init()
info = pygame.display.Info()
sw, sh = info.current_w, info.current_h
screen = pygame.display.set_mode((sw, sh), pygame.NOFRAME)
clock = pygame.time.Clock()

font_ui = pygame.font.SysFont("Arial Rounded MT Bold", 35)
font_debug_tiny = pygame.font.SysFont("Arial", 11, bold=True)
font_debug_bold = pygame.font.SysFont("Consolas", 18, bold=True)

cap = cv2.VideoCapture(selected_source)
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1, min_detection_confidence=0.5)

current_state, debug_mode, blink_count, is_blinked = 0, False, 0, False
ear_history = []

# --- Create Birds ---
my_birds = [
    Bird("octo", (200, 400), 4, 1),  # Name, (x, y), total frames
    Bird("blue", (1400,500),9, 2)
]

# --- MAIN LOOP ---
while True:
    start_time = time.time()
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: pygame.quit(); exit()
            if event.key == pygame.K_d: debug_mode = not debug_mode
        if event.type == pygame.MOUSEBUTTONDOWN and current_state == 0: current_state = 1

    success, frame = cap.read()
    if not success:
        if not is_live: cap.set(cv2.CAP_PROP_POS_FRAMES, 0); continue
        continue

    frame = cv2.flip(frame, 1) # FLIP THEM PATTIES

    vw, vh = int(cap.get(3)), int(cap.get(4))
    aspect = vw / vh
    nw, nh = (sw, int(sw / aspect)) if sw / sh < aspect else (int(sh * aspect), sh)
    ox, oy = (sw - nw) // 2, (sh - nh) // 2
    frame_res = cv2.resize(frame, (nw, nh))
    rgb_frame = cv2.cvtColor(frame_res, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)
    video_surf = pygame.surfarray.make_surface(np.transpose(rgb_frame, (1, 0, 2)))

    screen.fill((15, 15, 15))
    screen.blit(video_surf, (ox, oy))

    if current_state == 1:
        current_ear, is_blinking = 0.0, False
        if results and results.multi_face_landmarks:
            face_lms = results.multi_face_landmarks[0]
            current_ear = get_ear(face_lms, nw, nh)
            ear_history.append(current_ear)
            if len(ear_history) > 100: ear_history.pop(0)

            is_blinking = current_ear < 0.22

            if is_blinking and not is_blinked:
                blink_count += 1
                is_blinked = True
            elif not is_blinking:
                is_blinked = False

            # Tell the birds whether you are blinking right now
            for b in my_birds:
                b.trigger_dance(is_blinking)
                b.update()  # Always updates (handles returning to idle)
                b.draw(screen)  # Always visible

            if debug_mode:
                #
                # DRAW ALL LANDMARKS
                for i, lm in enumerate(face_lms.landmark):
                    px, py = int(lm.x * nw) + ox, int(lm.y * nh) + oy

                    # Highlight selection logic
                    if i in IRIS_INDICES:
                        pygame.draw.circle(screen, C_IRIS, (px, py), 2)
                        lbl = font_debug_tiny.render(str(i), True, C_IRIS)
                        screen.blit(lbl, (px + 3, py - 3))
                    elif i in EYELID_INDICES:
                        pygame.draw.circle(screen, C_EYE, (px, py), 2)
                        lbl = font_debug_tiny.render(str(i), True, C_EYE)
                        screen.blit(lbl, (px + 3, py - 3))
                    else:
                        # Non-essential points are just dots
                        pygame.draw.circle(screen, (70, 70, 70), (px, py), 1)
        #else:
            # EXTENDED DEBUG STATS
            end_time = time.time()
            latency = (end_time - start_time) * 1000
            stats = [
                f"FPS: {int(clock.get_fps())}",
                f"LATENCY: {latency:.1f}ms",
                f"RESOLUTION: {vw}x{vh}",
                f"IRIS LOCK: {'YES' if results.multi_face_landmarks else 'NO'}",
                f"BLINK STATE: {'BLINKING' if is_blinking else 'EYES OPEN'}"
            ]
            for i, s in enumerate(stats):
                screen.blit(font_debug_bold.render(s, True, C_GRAPH), (sw - 280, 40 + i * 28))

            # ENHANCED EAR GRAPH
            graph_rect = pygame.Rect(sw // 2 - 200, sh - 120, 400, 80)
            pygame.draw.rect(screen, (0, 0, 0, 200), graph_rect)
            pygame.draw.rect(screen, C_GRAPH, graph_rect, 1)
            if len(ear_history) > 2:
                pts = [(graph_rect.x + i * 4, graph_rect.bottom - v * 220) for i, v in enumerate(ear_history)]
                pygame.draw.lines(screen, C_GRAPH, False, pts, 2)
                # Dynamic Threshold Line
                pygame.draw.line(screen, C_DEBUG, (graph_rect.x, graph_rect.bottom - 0.22 * 220),
                                 (graph_rect.right, graph_rect.bottom - 0.22 * 220), 2)
                screen.blit(font_debug_tiny.render("0.22 THRESHOLD", True, C_DEBUG),
                            (graph_rect.right + 5, graph_rect.bottom - 0.22 * 220 - 5))

        # MAIN HUD
        hud_rect = pygame.Rect(ox + 40, oy + 40, 320, 110)
        pygame.draw.rect(screen, (255, 255, 255, 190), hud_rect, border_radius=15)
        screen.blit(font_ui.render(f"Blinks: {blink_count}", True, (30, 30, 30)), (hud_rect.x + 25, hud_rect.y + 15))
        screen.blit(font_ui.render(f"EAR: {current_ear:.4f}", True, (30, 30, 30)), (hud_rect.x + 25, hud_rect.y + 60))
        for b in my_birds:
            b.update()
            b.draw(screen)

    pygame.display.flip()
    clock.tick(30)