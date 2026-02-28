import pygame
import os


def load_asset(filename, size=None):
    path = os.path.join("assets", filename)
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    return None


class Bird:
    def __init__(self, name, pos, total_frames, loop_start_frame=1, animation_speed=0.2, scale=1.0):
        self.name = name
        self.pos = list(pos)
        self.frames = []
        self.animation_speed = animation_speed
        self.loop_index = loop_start_frame

        # 1. Load the first frame (index 0) to determine original size
        temp_img = load_asset(f"{name}-0.png")
        if temp_img:
            orig_w, orig_h = temp_img.get_size()
            # 2. Apply your scale multiplier (e.g., 2.5)
            new_size = (int(orig_w * scale), int(orig_h * scale))

            # 3. Load all frames starting from 0
            # range(total_frames) for 4 frames will give 0, 1, 2, 3
            for i in range(total_frames):
                frame = load_asset(f"{name}-{i}.png", size=new_size)
                if frame:
                    self.frames.append(frame)

        self.current_frame = 0.0
        self.is_dancing = False

    def trigger_dance(self, state):
        self.is_dancing = state

    def update(self):
        if self.is_dancing and len(self.frames) > 1:
            self.current_frame += self.animation_speed
            if self.current_frame >= len(self.frames):
                # Loops back to your chosen loop_index (usually 1)
                self.current_frame = float(self.loop_index)
        else:
            # When not blinking, it resets to frame 0 (your idle pose)
            self.current_frame = 0.0

    def draw(self, screen):
        if self.frames:
            img = self.frames[int(self.current_frame)]
            screen.blit(img, self.pos)