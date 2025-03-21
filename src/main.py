import pygame
from moviepy.editor import VideoFileClip
import time
from threading import Thread
import tempfile
import os
import sys

class VideoPlayer:
    def __init__(self, videoFile):
        pygame.init()

        self.clip = VideoFileClip(videoFile)
        self.width, self.height = self.clip.size
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.running = False
        self.paused = False
        self.startTime = 0
        self.pauseTime = 0
        self.lastFrame = None

        icon = pygame.image.load("ico/icon.png")
        pygame.display.set_caption("Medium Player")
        pygame.display.set_icon(icon)

        self.tempAudioPath = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        self.clip.audio.write_audiofile(self.tempAudioPath, logger=None)
        pygame.mixer.init()
        pygame.mixer.music.load(self.tempAudioPath)

    def play(self):
        self.running = True
        self.startTime = time.time()

        audioThread = Thread(target=self.playAudio)
        audioThread.start()

        self.playVideo()

    def playAudio(self):
        pygame.mixer.music.play()

    def playVideo(self):
        while self.running:
            self.screen.fill((0, 0, 0))

            if not self.paused:
                currentTime = time.time() - self.startTime

                if currentTime > self.clip.duration:
                    self.running = False
                    break

                frame = self.clip.get_frame(currentTime)
                self.lastFrame = frame
                frameSurface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                self.screen.blit(frameSurface, (0, 0))
            else:
                if self.lastFrame is not None:
                    frameSurface = pygame.surfarray.make_surface(self.lastFrame.swapaxes(0, 1))
                    self.screen.blit(frameSurface, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.togglePause()
                    elif event.key == pygame.K_RIGHT:
                        self.skip(0, 5)
                    elif event.key == pygame.K_LEFT:
                        self.skip(0, -5)
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

            pygame.display.update()
            self.clock.tick(30)

        self.cleanup()

    def togglePause(self):
        if self.paused:
            self.paused = False
            pygame.mixer.music.unpause()
            self.startTime += time.time() - self.pauseTime
        else:
            self.paused = True
            pygame.mixer.music.pause()
            self.pauseTime = time.time()

    def skip(self, minutes, seconds):
        skipTime = (minutes * 60 + seconds)
        newStartTime = time.time() - self.startTime + skipTime

        if newStartTime < 0:
            self.startTime = time.time()
            pygame.mixer.music.rewind()
        elif newStartTime > self.clip.duration:
            self.startTime = time.time() - self.clip.duration
            pygame.mixer.music.stop()
        else:
            self.startTime -= skipTime
            pygame.mixer.music.set_pos(newStartTime)

    def cleanup(self):
        pygame.quit()
        pygame.mixer.quit()
        if os.path.exists(self.tempAudioPath):
            os.remove(self.tempAudioPath)

if len(sys.argv) != 2:
    print("Usage: medpla <file path>")
else:
    videoPlayer = VideoPlayer(sys.argv[1])
    videoPlayer.play()