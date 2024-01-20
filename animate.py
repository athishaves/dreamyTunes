import pygame
import pygame.camera
import cv2
import json
import math
import sys
import os
import time

# ***************************** INITIAL CHECK *****************************

if len(sys.argv) != 4:
  print("USAGE : {} {} {} {}".format(sys.argv[0], "<INPUT-FILE>", "<BG-PATH>", "<LOGO-PATH>"))
  exit(0)

file_path = sys.argv[1]
BG_PATH = sys.argv[2]
LOGO_PATH = sys.argv[3]

# ***************************** CLASSES *****************************

GLOW_DEPTH = 76
GLOW_FACTOR = 25
GLOW_TRANSPARENCY = 4

class Ball:
  def __init__(self, screen, radius, color, pos):
    self.screen = screen
    self.radius = radius
    self.color = color
    self.pos = pos

    self.glow_depth = 0

    self.display()
  
  def move(self, pos):
    self.pos = pos
    self.display()
  
  def display(self):
    rad = self.radius
    color = self.color
    x, y = self.pos

    for i in range(1, self.glow_depth):
      i = i / GLOW_FACTOR / 2

      GLOW_RADIUS = rad + (rad * i)

      glow_surface = pygame.Surface((2*GLOW_RADIUS, 2*GLOW_RADIUS), pygame.SRCALPHA)

      pygame.draw.circle(glow_surface, (color[0], color[1], color[2], GLOW_TRANSPARENCY), (GLOW_RADIUS, GLOW_RADIUS), GLOW_RADIUS)

      screen.blit(glow_surface, (x - GLOW_RADIUS, y - GLOW_RADIUS))
    
    self.glow_depth -= 1

    pygame.draw.circle(self.screen, self.color, self.pos, self.radius)
    pygame.draw.circle(self.screen, 'white', self.pos, self.radius, TAIL_WIDTH // 2)

  def set_color(self, color):
    self.color = color
    self.glow_depth = GLOW_DEPTH
  
  def is_not_glown(self):
    return self.glow_depth <= 0

  def get_pos(self): return self.pos

class Rect:
  def __init__(self, screen, dimen, colors, pos, ts):
    self.screen = screen
    self.colors = colors
    self.color_index = 0
    self.time = ts

    w, h = dimen
    x, y = pos
    self.bound = (x, y, w, h)
    self.original_pos = pos

    self.display()
  
  def move_to(self, pos):
    _, _, w, h = self.bound
    x, y = pos
    self.bound = (x, y, w, h)
    self.display()
  
  def move(self, delta):
    delta_x, delta_y = delta
    x, y, w, h = self.bound
    x, y = self.original_pos
    x += delta_x
    y += delta_y
    self.bound = (x, y, w, h)

    if x + w >= -SCREEN_WIDTH / 4 and x <= SCREEN_WIDTH * 1.25: self.display()

  def change_color(self):
    if self.color_index == 0:
      self.color_index = 1
      self.glow_depth = GLOW_DEPTH
  
  def display(self):
    color = self.colors[self.color_index]
    x, y, width, height = self.bound

    if self.color_index != 0:

      for i in range(1, self.glow_depth):
        i = i / GLOW_FACTOR

        GLOW_WIDTH = width + (height * i)
        GLOW_HEIGHT = height + (height * i)

        glow_surface = pygame.Surface((GLOW_WIDTH, GLOW_HEIGHT), pygame.SRCALPHA)

        pygame.draw.rect(glow_surface, (color[0], color[1], color[2], GLOW_TRANSPARENCY), (0, 0, GLOW_WIDTH, GLOW_HEIGHT))
        # pygame.draw.rect(glow_surface, (255, 255, 255, GLOW_TRANSPARENCY), (0, 0, GLOW_WIDTH, GLOW_HEIGHT))
        screen.blit(glow_surface, (x - (GLOW_WIDTH - width) / 2, y - (GLOW_HEIGHT - height) / 2))
      
      self.glow_depth -= 1

    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(surface, color, (0,0,width,height))
    screen.blit(surface, (x,y))
  
  def is_not_glown(self):
    return self.glow_depth <= 0

class Tail:
  def __init__(self, screen, color, width, threshold_offset):
    self.points = []
    self.THRESHOLD = SCREEN_WIDTH / 2 - (SCREEN_WIDTH / 17.5) - threshold_offset
    self.screen = screen
    self.color = color
    self.width = width

    self.display()
  
  def add_point(self, pos):
    self.points.append(pos)
    while len(self.points) > 0 and self.points[0][0] < self.THRESHOLD: self.remove_tail()
  
  def move(self, delta):
    delta_x, delta_y = delta

    for i in range(len(self.points)):
      x, y = self.points[i]
      self.points[i] = ( x + delta_x, y + delta_y )
    
    self.display()
  
  def remove_tail(self):
    if len(self.points) > 0: self.points.pop(0)
    return len(self.points) > 0
  
  def display(self):
    if len(self.points) > 2: pygame.draw.lines(self.screen, self.color, False, self.points, self.width)
    # for i in range(1, len(self.points)):
    #   prev = self.points[i-1]
    #   cur = self.points[i]
    #   pygame.draw.line(self.screen, self.color, prev, cur, self.width)

class Logo:
  def __init__(self, screen, logo_path, pos):
    self.screen = screen
    self.pos = pos

    LOGO_FACTOR = 10

    self.logo = pygame.image.load(logo_path)
    self.logo = pygame.transform.scale(self.logo, (SCREEN_HEIGHT // LOGO_FACTOR, SCREEN_HEIGHT // LOGO_FACTOR))
    self.logo = self.logo.convert_alpha()

    self.display()
  
  def move(self, delta):
    delta_x, delta_y = delta
    x, y = self.pos
    self.pos = (x+delta_x, y+delta_y)
    
    self.display()
  
  def display(self):
    self.screen.blit(self.logo, self.pos)

# ***************************** INITIALISE *****************************

print("INITIATING...")

start_time = time.time()

pygame.init()
pygame.camera.init()


try:
  TEMPO = float(input("Set the tempo => "))
except:
  TEMPO = 1

SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
TIME_HORIZONTAL, TIME_VERTICAL = 10, 30

BACKGROUND_COLOR = (100,100,100)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen.fill(BACKGROUND_COLOR)

bg = pygame.image.load(BG_PATH)

initial_display_bg = pygame.Rect(0, 0, SCREEN_WIDTH / 2, SCREEN_HEIGHT)
final_display_bg = pygame.Rect(SCREEN_WIDTH, 0, SCREEN_WIDTH / 2, SCREEN_HEIGHT)
screen.blit(bg, initial_display_bg)

FPS = 60

temp_file = 'final.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter(temp_file, fourcc, FPS, (SCREEN_WIDTH, SCREEN_HEIGHT))

# ***************************** COLORS *****************************

vibrant_colors_rgb = [
  (0, 80, 255),      # Electric Blue (#0050FF)
  (57, 255, 20),     # Neon Green (#39FF14)
  (255, 0, 255),     # Fuchsia (#FF00FF)
  (127, 255, 0),     # Chartreuse (#7FFF00)
  (255, 105, 180),   # Hot Pink (#FF69B4)
  (50, 205, 50),     # Lime Green (#32CD32)
  (255, 215, 0),     # Sunshine Yellow (#FFD700)
  (255, 127, 80),    # Coral (#FF7F50)
  (255, 244, 79),    # Lemon Yellow (#FFF44F)
  (218, 112, 214),   # Orchid (#DA70D6)
  (0, 201, 87),      # Emerald Green (#00C957)
  (0, 255, 0),       # Grass Green (#00FF00)
  # (227, 66, 52),     # Vermilion (#E34234)
  (255, 160, 82),    # Marigold (#FFA052)
  (0, 127, 255),     # Azure (#007FFF)
  (0, 255, 255),     # Cyan (#00FFFF)
  (0, 0, 255),       # Blue (#0000FF)
  # (255, 0, 0),       # Red (#FF0000)
  (0, 128, 128),     # Teal (#008080)
  (128, 0, 128),     # Purple (#800080)
  (255, 140, 0),     # Dark Orange (#FF8C00)
  (0, 255, 128),     # Spring Green (#00FF80)
  (255, 255, 0),     # Yellow (#FFFF00)
  (128, 128, 0),     # Olive (#808000)
  (255, 20, 147),    # Deep Pink (#FF1493)
]

vibrant_colors_rgb = list(set(vibrant_colors_rgb))

import random

note_colors = {}

def get_random_color(note):
  if note in note_colors: return note_colors[note]
  color = vibrant_colors_rgb.pop(random.randint(0, len(vibrant_colors_rgb)-1))
  note_colors[note] = color
  return color

# ***************************** READ MIDI JSON *****************************

print("CALCULATING POSITIONS")

with open(file_path + '.json') as f: data = json.load(f)


BALL_RADIUS = int(SCREEN_HEIGHT / 80)
TAIL_WIDTH = int(BALL_RADIUS / 4)

OFFSET_HORIZONTAL = SCREEN_WIDTH / 2
OFFSET_VERTICAL = SCREEN_HEIGHT / 2

try:
  TRACK = int(input("Set the track => "))
except:
  TRACK = 0

# TEMPO = TEMPO / data['tempo'][0]['bpm']
total_time = data['tracks'][TRACK]['duration'] / TEMPO
notes = data['tracks'][TRACK]['notes']

prev_ts = 0
last_ts, last_dur = None, None

ball_positions = []
base_objects = []
logo_positions = []

BASE_COLOR = (255, 255, 255, 25)

for note in notes:
  name = note['name']
  ts = note['time']
  ts = ts / TEMPO
  duration = note['duration']

  # OBJECT

  if last_ts == ts: continue

  HORIZONTAL_SQEEZE = 0.9

  WIDTH_PARAM = HORIZONTAL_SQEEZE * SCREEN_WIDTH / TIME_HORIZONTAL
  width = min(duration, 0.5) * WIDTH_PARAM
  
  height = SCREEN_HEIGHT / 100
  
  x = (ts * HORIZONTAL_SQEEZE * SCREEN_WIDTH / TIME_HORIZONTAL) + OFFSET_HORIZONTAL
  y = (ts - prev_ts) * 1.5 * SCREEN_HEIGHT / TIME_VERTICAL + OFFSET_VERTICAL

  # if last_ts is not None and (ts - (last_ts + last_dur) >= 1):
  #   new_y = (ts - prev_ts) * 1.5 * SCREEN_HEIGHT / TIME_VERTICAL + OFFSET_VERTICAL
  #   OFFSET_VERTICAL += (new_y - y)
  #   y = new_y

  last_ts, last_dur = ts, duration

  x_center = x + (width * 0.6)
  y_center = y + (height / 2)

  rand_color = get_random_color(name)
  rect = Rect(screen, (width, height), [BASE_COLOR, rand_color], (x,y), ts)
  base_objects.append(rect)

  # BALL POS

  x = x_center
  y = y - BALL_RADIUS

  ball_positions.append((x,y,ts,rand_color))

new_ball_positions = [ball_positions[0]]
logo_count = 0
LOGO_VERTICAL_OFFSET = SCREEN_HEIGHT * 0.2
logo_flag = True

for i in range(1, len(ball_positions)):
  prev_x, prev_y, prev_ts, prev_color = ball_positions[i-1]
  x, y, ts, _ = ball_positions[i]

  mid = (
    prev_x + (x - prev_x) * 0.5,
    prev_y - min((y - prev_y) * 0.5, (SCREEN_HEIGHT / 20)),
    (ts + prev_ts) / 2,
    prev_color
  )

  new_ball_positions.append(mid)
  new_ball_positions.append(ball_positions[i])
  logo_count += 2

  if logo_count >= 100:
    logo_count = 0
    offset = LOGO_VERTICAL_OFFSET if logo_flag else -1.5 * LOGO_VERTICAL_OFFSET
    logo_flag = not logo_flag
    logo_positions.append(Logo(screen, LOGO_PATH, (x, y+offset)))

ball_positions = new_ball_positions

new_ball_pos = 0
if ball_positions[0][2] != 0: 
  new_ball_pos = SCREEN_WIDTH * 0.02
  ball_positions.insert(0, (SCREEN_WIDTH * 0.5 - new_ball_pos, SCREEN_HEIGHT * 0.4, 0, 'white'))
  new_ball_pos += SCREEN_WIDTH * 0.02

# ***************************** PLAY *****************************

# UPDATE
pygame.display.update()

print("GENERATING VIDEO")

start = 1
note_index = 0

frame_count = 0
FRAME_TIME = 1.0 / FPS

init_x, init_y, _, color = ball_positions[0]
camera = (init_x, init_y)
ball = Ball(screen, BALL_RADIUS, color, camera)
tail = Tail(screen, 'white', TAIL_WIDTH, new_ball_pos)

def update_progress(i, n):
  percent = i / n * 100
  print(("=" * int(percent)) + (" " * (100 - int(percent))), str(int(i)) + "/" + str(int(n)), "{}%".format(int(percent)), end='\r')

def write_to_file():
  screenshot = pygame.surfarray.array3d(screen)
  screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

  rotated_and_flipped_frame = cv2.rotate(screenshot, cv2.ROTATE_90_CLOCKWISE)
  rotated_and_flipped_frame = cv2.flip(rotated_and_flipped_frame, 1)

  video.write(rotated_and_flipped_frame)

EASE_IN = 2.25
def ease_in(alpha): return math.pow(alpha, EASE_IN)
EASE_OUT = 1.75
def ease_out(alpha): return 1 - math.pow(1-alpha, EASE_OUT)

def alpha(left, right, cur):
  if left == right: return 1
  return (cur - left) / (right - left)

def interpolation(left, right, cur):
  prev_x, prev_y, prev_ts, prev_color = left
  next_x, next_y, next_ts, _ = right
  
  a = alpha(prev_ts, next_ts, cur)

  if prev_y < next_y: # UP
    x = prev_x + a * (next_x - prev_x)
    y = prev_y + ease_in(a) * (next_y - prev_y)
  else: # DOWN
    x = prev_x + a * (next_x - prev_x)
    y = prev_y + ease_out(a) * (next_y - prev_y)

  return x, y, prev_color

while True:
  sec, ms = frame_count // FPS, FRAME_TIME * (frame_count % FPS)
  cur = sec + ms

  update_progress(cur, total_time)

  base_tapped = cur >= base_objects[note_index].time
  if base_tapped:
    base_objects[note_index].change_color()
    note_index += 1

  # while start < len(ball_positions) and cur >= ball_positions[start][2]: start += 1
  if cur >= ball_positions[start][2]: start += 1

  if start >= len(ball_positions): 
    for base in base_objects: base.change_color()
    ball.set_color(ball_positions[-1][3])
    break

  left = ball_positions[start - 1]
  right = ball_positions[start]
  
  x, y, color = interpolation(left, right, cur)
  if base_tapped: ball.set_color(color)

  screen.fill(BACKGROUND_COLOR)

  interpolation_factor = cur / total_time
  interpolated_rect = pygame.Rect(
    int(initial_display_bg.left - (final_display_bg.left - initial_display_bg.left) * interpolation_factor),
    int(initial_display_bg.top - (final_display_bg.top - initial_display_bg.top) * interpolation_factor),
    initial_display_bg.width,
    initial_display_bg.height
  )
  screen.blit(bg, interpolated_rect)

  camera_x, camera_y = camera
  delta_x, delta_y = x - camera_x, y - camera_y

  # tail.move((-delta_x, -delta_y))
  small_delta = (init_x-x, init_y-y)
  tail.move(small_delta)
  tail.add_point(camera)
  init_x, init_y = x, y

  for rect in base_objects: rect.move((-delta_x, -delta_y))
  for logo in logo_positions: logo.move(small_delta)
  # ball.set_color(color)
  ball.display()
  pygame.display.update()

  write_to_file()

  frame_count += 1


# REMOVE TAIL
while tail.remove_tail() or not rect.is_not_glown() or not ball.is_not_glown():
  screen.fill(BACKGROUND_COLOR)
  screen.blit(bg, interpolated_rect)
  
  tail.display()
  for rect in base_objects: rect.display()
  for logo in logo_positions: logo.display()
  ball.display()

  pygame.display.update()

  write_to_file()

for i in range(FPS // 3): write_to_file()

update_progress(total_time, total_time)
print()

video.release()

pygame.quit()

# ***************************** ATTACH AUDIO *****************************

print("ATTACHING AUDIO")

audio_file = file_path + ".wav"
output_file = file_path + "-audio" + ".mp4"
command = "ffmpeg -i {} -i {} -c:v copy -c:a aac -strict experimental {} -y >/dev/null 2>&1".format(temp_file, audio_file, output_file)
os.system(command)

command = "rm {}".format(temp_file)
os.system(command)

command = "mv {} {}".format(output_file, temp_file)
os.system(command)
output_file = temp_file

# ***************************** END *****************************

print("SAVED AS {}".format(output_file))
print("Program took {} seconds".format(int(time.time() - start_time)))
