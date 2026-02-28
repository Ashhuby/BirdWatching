import pygame
import os


def load_asset(filename, size=None):
    """Helper to load images from the assets folder."""
    path = os.path.join("assets", filename)
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    return None


class Bird:
    def __init__(self, name, pos, frame_count):
        self.name = name
        self.pos = list(pos)
        self.frames = []

        # Load all frames: birdname1.png, birdname2.png, etc.
        for i in range(1, frame_count + 1):
            frame = load_asset(f"{name}{i}.png", size=(150, 150))
            if frame:
                self.frames.append(frame)

        self.current_frame = 0.0
        self.is_dancing = False
        self.animation_speed = 0.25  # Adjust for faster/slower dance

    def trigger_dance(self):
        """Starts the animation if it isn't already running."""
        if not self.is_dancing and len(self.frames) > 1:
            self.is_dancing = True
            self.current_frame = 1.0  # Skip frame 0 (idle) to start dance

    def update(self):
        """Handles the animation logic."""
        if self.is_dancing:
            self.current_frame += self.animation_speed
            # If we reach the end of the frames, return to idle
            if self.current_frame >= len(self.frames):
                self.current_frame = 0.0
                self.is_dancing = False
        else:
            self.current_frame = 0.0  # Force idle frame

    def draw(self, screen):
        """Draws the current frame to the screen."""
        if self.frames:
            # Convert float index to int for list access
            img = self.frames[int(self.current_frame)]
            screen.blit(img, self.pos)