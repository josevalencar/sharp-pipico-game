import sys
import random
import time
from enum import Enum, auto

import pygame
import serial 

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

SESSION_DURATION = 30.0
TARGET_DURATION = 2.0
TARGET_TOLERANCE = 0.06

SERIAL_PORT = "/dev/cu.usbmodem11401"
SERIAL_BAUDRATE = 115200

class DistanceInput:
    def update(self):
        pass

    def get_value(self) -> float:
        raise NotImplementedError


class KeyboardDistanceInput(DistanceInput):
    def __init__(self, initial=0.5, step=0.01):
        self.value = initial
        self.step = step

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.value += self.step
        if keys[pygame.K_DOWN]:
            self.value -= self.step
        self.value = max(0.0, min(1.0, self.value))

    def get_value(self) -> float:
        return self.value


class SerialDistanceInput(DistanceInput):
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 0.0):
        self.port_name = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.value = 0.5

        try:
            self.ser = serial.Serial(
                self.port_name,
                self.baudrate,
                timeout=self.timeout
            )
            time.sleep(2.0)
            print(f"Serial aberta em {self.port_name}")
        except serial.SerialException as e:
            print(f"Erro ao abrir porta serial {self.port_name}: {e}")
            print("Usando KeyboardDistanceInput como fallback.")
            self.ser = None

    def update(self):
        if self.ser is None or not self.ser.is_open:
            return

        try:
            while True:
                line = self.ser.readline()
                if not line:
                    break
                try:
                    s = line.decode("utf-8").strip()
                    if not s:
                        continue
                    v = float(s)
                    v = max(0.0, min(1.0, v))
                    self.value = v
                except ValueError:
                    continue
        except serial.SerialException as e:
            print(f"Erro de leitura serial: {e}")

    def get_value(self) -> float:
        return self.value

class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    GAME_OVER = auto()

class DistanceTargetComboGame:
    def __init__(self, screen, distance_input: DistanceInput):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.distance_input = distance_input

        self.state = GameState.MENU

        self.session_time = 0.0
        self.current_target = 0.5
        self.target_timer = 0.0
        self.target_hit_this_round = False

        self.score = 0
        self.total_targets = 0
        self.hits = 0
        self.streak = 0
        self.best_streak = 0

        self.font_small = pygame.font.SysFont("arial", 22)
        self.font_medium = pygame.font.SysFont("arial", 32, bold=True)
        self.font_large = pygame.font.SysFont("arial", 56, bold=True)

    def reset_session(self):
        self.session_time = 0.0
        self.target_timer = 0.0
        self.current_target = random.uniform(0.1, 0.9)
        self.target_hit_this_round = False

        self.score = 0
        self.total_targets = 0
        self.hits = 0
        self.streak = 0
        self.best_streak = 0

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.render()
            pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_SPACE:
                        self.reset_session()
                        self.state = GameState.PLAYING
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.reset_session()
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU

    def update(self, dt: float):
        self.distance_input.update()

        if self.state == GameState.MENU:
            return

        if self.state == GameState.PLAYING:
            self.session_time += dt
            self.target_timer += dt

            if self.target_timer >= TARGET_DURATION:
                self.next_target()

            value = self.distance_input.get_value()

            if not self.target_hit_this_round:
                if abs(value - self.current_target) <= TARGET_TOLERANCE:
                    self.register_hit()

            if self.session_time >= SESSION_DURATION:
                self.state = GameState.GAME_OVER

    def next_target(self):
        if not self.target_hit_this_round:
            self.streak = 0
        
        self.target_timer = 0.0
        self.current_target = random.uniform(0.1, 0.9)
        self.target_hit_this_round = False
        self.total_targets += 1

    def register_hit(self):
        self.target_hit_this_round = True
        self.hits += 1
        self.streak += 1
        self.best_streak = max(self.best_streak, self.streak)

        base_points = 100
        bonus = int(self.streak * 10)
        self.score += base_points + bonus

    def render(self):
        if self.state == GameState.MENU:
            self.render_menu()
        elif self.state == GameState.PLAYING:
            self.render_playing()
        elif self.state == GameState.GAME_OVER:
            self.render_game_over()

    def draw_background(self):
        top_color = (25, 35, 60)
        bottom_color = (5, 5, 10)

        for y in range(SCREEN_HEIGHT):
            t = y / SCREEN_HEIGHT
            r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
            g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
            b = int(top_color[2] * (1 - t) + bottom_color[2] * t)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

    def render_menu(self):
        self.draw_background()

        title = self.font_large.render("Distance Target Combo", True, (240, 240, 255))
        hint = self.font_medium.render("Pressione ESPAÇO para iniciar", True, (200, 200, 220))
        control1 = self.font_small.render("Controles:", True, (210, 210, 230))
        control2 = self.font_small.render("Mão no sensor IR (Sharp) para mover o marcador", True, (190, 190, 210))
        control3 = self.font_small.render("Ou use ↑ e ↓ no teclado se estiver em modo teclado", True, (190, 190, 210))

        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 160))
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 240))
        self.screen.blit(control1, (SCREEN_WIDTH // 2 - control1.get_width() // 2, 320))
        self.screen.blit(control2, (SCREEN_WIDTH // 2 - control2.get_width() // 2, 350))
        self.screen.blit(control3, (SCREEN_WIDTH // 2 - control3.get_width() // 2, 380))

    def render_playing(self):
        self.draw_background()

        value = self.distance_input.get_value()
        time_left = max(0.0, SESSION_DURATION - self.session_time)
        center_x = SCREEN_WIDTH // 2

        hud_score = self.font_medium.render(f"Score: {self.score}", True, (240, 240, 255))
        hud_time = self.font_medium.render(f"Tempo: {time_left:4.1f}s", True, (240, 240, 255))
        hud_hits = self.font_small.render(f"Alvos acertados: {self.hits}", True, (210, 210, 230))
        hud_streak = self.font_small.render(f"Streak: {self.streak}", True, (210, 210, 230))

        self.screen.blit(hud_score, (40, 30))
        self.screen.blit(hud_time, (SCREEN_WIDTH - hud_time.get_width() - 40, 30))
        self.screen.blit(hud_hits, (40, 80))
        self.screen.blit(hud_streak, (40, 110))

        bar_width = 40
        bar_height = SCREEN_HEIGHT * 0.7
        
        bar_x = (SCREEN_WIDTH - bar_width) / 2
        bar_y = (SCREEN_HEIGHT - bar_height) / 2

        pygame.draw.rect(self.screen, (40, 40, 70), 
                         (bar_x - 4, bar_y - 4, bar_width + 8, bar_height + 8), 
                         border_radius=12)
        pygame.draw.rect(self.screen, (70, 80, 110), 
                         (bar_x, bar_y, bar_width, bar_height), 
                         border_radius=10)

        target_y = bar_y + (self.current_target * bar_height)
        
        pygame.draw.line(self.screen, (255, 200, 50), 
                         (bar_x - 10, target_y), 
                         (bar_x + bar_width + 10, target_y), 
                         3)

        marker_y = bar_y + (value * bar_height)
        marker_x = bar_x + bar_width / 2

        inside_target = abs(value - self.current_target) <= TARGET_TOLERANCE

        if inside_target:
            marker_color_outer = (120, 255, 120)
            marker_color_inner = (20, 230, 20)
        else:
            marker_color_outer = (180, 180, 240)
            marker_color_inner = (230, 230, 255)

        pygame.draw.circle(self.screen, marker_color_outer, (int(marker_x), int(marker_y)), 16)
        pygame.draw.circle(self.screen, marker_color_inner, (int(marker_x), int(marker_y)), 10)

        tolerance_px = TARGET_TOLERANCE * bar_height
        pygame.draw.rect(
            self.screen,
            (255, 255, 255, 40),
            (bar_x, target_y - tolerance_px, bar_width, 2 * tolerance_px),
            width=1
        )

        txt_value = self.font_small.render(f"Valor: {value:.3f}", True, (220, 220, 235))
        txt_target = self.font_small.render(f"Alvo: {self.current_target:.3f}", True, (220, 220, 235))
        
        self.screen.blit(txt_value, (bar_x + bar_width + 20, marker_y - 10))
        self.screen.blit(txt_target, (bar_x + bar_width + 20, target_y - 10))

        txt_info = self.font_small.render("Ajuste a mão para subir/descer o marcador", True, (200, 200, 220))
        self.screen.blit(txt_info, (center_x - txt_info.get_width() // 2, bar_y + bar_height + 30))

    def render_game_over(self):
        self.draw_background()

        center_x = SCREEN_WIDTH // 2

        title = self.font_large.render("Fim da partida", True, (240, 240, 255))
        score_text = self.font_medium.render(f"Score final: {self.score}", True, (230, 230, 245))
        hits_text = self.font_small.render(f"Alvos acertados: {self.hits}", True, (210, 210, 230))
        total_text = self.font_small.render(f"Total de alvos apresentados: {self.total_targets}", True, (210, 210, 230))
        streak_text = self.font_small.render(f"Melhor streak: {self.best_streak}", True, (210, 210, 230))

        instr1 = self.font_small.render("R - Recomeçar", True, (200, 200, 220))
        instr2 = self.font_small.render("ESC - Voltar ao menu", True, (200, 200, 220))

        self.screen.blit(title, (center_x - title.get_width() // 2, 140))
        self.screen.blit(score_text, (center_x - score_text.get_width() // 2, 210))
        self.screen.blit(hits_text, (center_x - hits_text.get_width() // 2, 260))
        self.screen.blit(total_text, (center_x - total_text.get_width() // 2, 290))
        self.screen.blit(streak_text, (center_x - streak_text.get_width() // 2, 320))

        self.screen.blit(instr1, (center_x - instr1.get_width() // 2, 380))
        self.screen.blit(instr2, (center_x - instr2.get_width() // 2, 410))

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Distance Target Combo")

    pygame.font.init()

    serial_input = SerialDistanceInput(SERIAL_PORT, SERIAL_BAUDRATE)
    if serial_input.ser is None:
        distance_input = KeyboardDistanceInput()
    else:
        distance_input = serial_input

    game = DistanceTargetComboGame(screen, distance_input)
    game.run()

if __name__ == "__main__":
    main()
