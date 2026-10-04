"""Prehnite Volley — neon vertical volley arcade for ElbowOS. Python 3 + pygame."""
import math
import os
import random
import subprocess
import sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/workspace/artifacts/PREHNITE_VOLLEY_ElbowOS.mp4")
INK = (7, 18, 16)
PREHN = (138, 255, 92)
AMBER = (255, 186, 62)
CORAL = (255, 96, 88)
CREAM = (236, 255, 214)
MINT = (46, 120, 92)
DEEP = (14, 42, 34)

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.Font(None, 72)
        self.small = pygame.font.Font(None, 42)
        self.tiny = pygame.font.Font(None, 32)
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            self.screen = pygame.Surface((W, H))
        pygame.display.set_caption("Prehnite Volley")
        self.bg = self._make_bg()
        self.reset(full=True)

    def _make_bg(self):
        bg = pygame.Surface((W, H))
        for y in range(H):
            t = y / H
            bg.fill((8 + int(10 * t), 22 + int(16 * (1 - t)), 18), (0, y, W, 1))
        for x in range(90, W, 90):
            pygame.draw.line(bg, (18, 48, 38), (x, 240), (x, 1680), 1)
        for y in range(280, 1680, 90):
            pygame.draw.line(bg, (18, 48, 38), (70, y), (W - 70, y), 1)
        pygame.draw.rect(bg, MINT, (60, 230, W - 120, 1460), 4, border_radius=18)
        pygame.draw.line(bg, (70, 140, 90), (60, H // 2), (W - 60, H // 2), 2)
        return bg

    def reset(self, full=False):
        if full:
            self.score = 0
            self.rival = 0
            self.combo = 1
            self.t = 0
        self.px = W / 2
        self.rx = W / 2
        self.ball = [W / 2, 760.0]
        ang = random.choice([-0.55, -0.25, 0.25, 0.55])
        spd = 16 + random.random() * 3
        self.vx = math.sin(ang) * spd
        self.vy = math.cos(ang) * spd
        if self.vy > 0:
            self.vy *= -1
        self.trail = []
        self.sparks = []
        self.flash = 0
        self.orbs = []
        for i in range(4):
            self.orbs.append([180 + i * 200, 820 + (i % 2) * 180, 1])

    def burst(self, x, y, color):
        for _ in range(10):
            a = random.random() * math.tau
            s = 2 + random.random() * 7
            self.sparks.append([x, y, math.cos(a) * s, math.sin(a) * s, color, 18])

    def update(self, keys=None, auto=False):
        self.t += 1
        target = self.ball[0] + self.vx * 5
        if auto:
            jitter = math.sin(self.t * 0.17) * 28
            self.px += max(-22, min(22, target + jitter - self.px))
        elif keys:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.px -= 24
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.px += 24
        self.px = max(160, min(W - 160, self.px))
        aim = self.ball[0] + self.vx * 4
        self.rx += max(-18, min(18, aim - self.rx))
        self.rx = max(160, min(W - 160, self.rx))
        self.ball[0] += self.vx
        self.ball[1] += self.vy
        self.trail.append((self.ball[0], self.ball[1]))
        self.trail = self.trail[-14:]
        if self.ball[0] < 96 or self.ball[0] > W - 96:
            self.vx *= -1
            self.ball[0] = max(96, min(W - 96, self.ball[0]))
            self.flash = 8
            self.burst(self.ball[0], self.ball[1], CORAL)
        if 1640 < self.ball[1] < 1710 and abs(self.ball[0] - self.px) < 150 and self.vy > 0:
            off = (self.ball[0] - self.px) / 150
            self.vy = -abs(self.vy) - 0.6
            self.vx = off * 14 + self.vx * 0.35
            self.combo = min(8, self.combo + 1)
            self.score += 10 * self.combo
            self.burst(self.ball[0], self.ball[1], PREHN)
        if 250 < self.ball[1] < 320 and abs(self.ball[0] - self.rx) < 140 and self.vy < 0:
            off = (self.ball[0] - self.rx) / 140
            self.vy = abs(self.vy) + 0.4
            self.vx = off * 12 + self.vx * 0.3
            self.burst(self.ball[0], self.ball[1], AMBER)
        spd = math.hypot(self.vx, self.vy)
        if spd > 28:
            self.vx *= 28 / spd
            self.vy *= 28 / spd
        if abs(self.vy) < 8:
            self.vy = 8 if self.vy >= 0 else -8
        if self.ball[1] > 1780:
            self.rival += 1
            self.combo = 1
            self.burst(self.ball[0], 1720, CORAL)
            self.reset()
            self.vy = -abs(self.vy)
        elif self.ball[1] < 180:
            self.score += 50 * self.combo
            self.burst(self.ball[0], 250, AMBER)
            self.reset()
            self.vy = abs(self.vy)
        alive = []
        for orb in self.orbs:
            if orb[2] and math.hypot(self.ball[0] - orb[0], self.ball[1] - orb[1]) < 36:
                orb[2] = 0
                self.score += 25 * self.combo
                self.burst(orb[0], orb[1], AMBER)
            else:
                alive.append(orb)
        self.orbs = alive
        if self.t % 90 == 0 and len(self.orbs) < 5:
            self.orbs.append([random.randint(180, 900), random.randint(640, 1200), 1])
        nxt = []
        for s in self.sparks:
            s[0] += s[2]
            s[1] += s[3]
            s[5] -= 1
            if s[5] > 0:
                nxt.append(s)
        self.sparks = nxt
        self.flash = max(0, self.flash - 1)

    def draw(self, surf):
        surf.blit(self.bg, (0, 0))
        pulse = 8 + int(6 * math.sin(self.t * 0.2))
        rail = CORAL if self.flash else (40 + pulse, 90, 70)
        pygame.draw.rect(surf, rail, (48, 230, 18, 1460), border_radius=8)
        pygame.draw.rect(surf, rail, (W - 66, 230, 18, 1460), border_radius=8)
        for i, (x, y) in enumerate(self.trail):
            pygame.draw.circle(surf, (60, 140, 70), (int(x), int(y)), 6 + i // 3)
        for orb in self.orbs:
            if not orb[2]:
                continue
            bob = math.sin(self.t * 0.1 + orb[0]) * 6
            pygame.draw.circle(surf, AMBER, (int(orb[0]), int(orb[1] + bob)), 18)
            pygame.draw.circle(surf, CREAM, (int(orb[0]), int(orb[1] + bob)), 8)
        pygame.draw.rect(surf, PREHN, (self.px - 130, 1668, 260, 28), border_radius=12)
        pygame.draw.rect(surf, CREAM, (self.px - 46, 1674, 92, 10), border_radius=5)
        pygame.draw.rect(surf, AMBER, (self.rx - 120, 268, 240, 26), border_radius=12)
        pygame.draw.circle(surf, CREAM, (int(self.ball[0]), int(self.ball[1])), 20)
        pygame.draw.circle(surf, PREHN, (int(self.ball[0]), int(self.ball[1])), 12)
        for s in self.sparks:
            pygame.draw.circle(surf, s[4], (int(s[0]), int(s[1])), 4)
        title = self.font.render("PREHNITE VOLLEY", True, PREHN)
        surf.blit(title, title.get_rect(center=(W // 2, 90)))
        sc = self.small.render(f"SCORE {self.score}   COMBO x{self.combo}", True, CREAM)
        surf.blit(sc, sc.get_rect(center=(W // 2, 160)))
        tag = self.tiny.render("x.com/ElbowOS", True, AMBER)
        surf.blit(tag, tag.get_rect(center=(W // 2, 1840)))
        hint = self.tiny.render("A / D  volley the prehnite", True, (160, 210, 170))
        surf.blit(hint, hint.get_rect(center=(W // 2, 1788)))

    def record(self):
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
            "-movflags", "+faststart", OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        frames = FPS * SECS
        for _ in range(frames):
            self.update(auto=True)
            self.draw(self.screen)
            proc.stdin.write(pygame.image.tostring(self.screen, "RGB"))
        proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1500:]}")
        print("wrote", OUT)

    def play(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
                    self.reset(full=True)
            self.update(keys=pygame.key.get_pressed(), auto=False)
            self.draw(self.screen)
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()

def main():
    random.seed(11)
    g = Game()
    if PLAY and not RECORD:
        g.play()
    else:
        g.record()
        pygame.quit()

if __name__ == "__main__":
    main()
