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
    def __init__(self, name, pos, total_frames, loop_start_frame=1, animation_speed=0.2):
        self.name = name
        self.pos = list(pos)
        self.frames = []

        # Load all frames
        for i in range(1, total_frames + 1):
            frame = load_asset(f"{name}{i}.png", size=(150, 150))
            if frame:
                self.frames.append(frame)

        self.current_frame = 0.0
        self.is_dancing = False
        # Use the variable passed in to control speed
        self.animation_speed = animation_speed
        self.loop_index = loop_start_frame

    def trigger_dance(self, state):
        """Sets the dance state based on external blink detection."""
        self.is_dancing = state

    def update(self):
        if self.is_dancing and len(self.frames) > 1:
            # The speed variable controls how fast we move through the frame list
            self.current_frame += self.animation_speed

            if self.current_frame >= len(self.frames):
                self.current_frame = float(self.loop_index)
        else:
            self.current_frame = 0.0

    def draw(self, screen):
        if self.frames:
            # Convert float to int to index the frame list
            img = self.frames[int(self.current_frame)]
            screen.blit(img, self.pos)