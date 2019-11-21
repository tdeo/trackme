import json
import logging
import time
import os
import shutil
import stat
import sys
import tempfile

import keyboard
from pynput import mouse
import platform

TIME_RANGE = 5 # time to group logs, in seconds

LOGGER = logging.getLogger('trackme')
LOGGER.setLevel(logging.DEBUG)

LOG_DIR = f'{os.environ.get("HOME")}/.trackme/logs'
os.makedirs(f'{LOG_DIR}/keyboard', exist_ok=True)
os.makedirs(f'{LOG_DIR}/mouse', exist_ok=True)
os.chown(f'{LOG_DIR}/keyboard', int(os.environ.get('SUDO_UID', -1)), int(os.environ.get('SUDO_GID', -1)))
os.chown(f'{LOG_DIR}/mouse', int(os.environ.get('SUDO_UID', -1)), int(os.environ.get('SUDO_GID', -1)))

class Keyboard:
  current = {}
  pressSinceRelease = False
  log = {}

  @classmethod
  def filename(cls, epoch):
    day = time.strftime("%Y-%m-%d", time.localtime(epoch))
    return f'{LOG_DIR}/keyboard/{day}.json'

  @classmethod
  def flush_log(cls, epoch):
    current = {}
    try:
      with open(cls.filename(epoch)) as f:
        current = json.load(f)
    except Exception as e:
      LOGGER.exception(e)

    if epoch not in current:
      current[epoch] = {}

    for e in cls.log[epoch]:
      key = ','.join(str(el) for el in e)
      if key not in current[epoch]:
        current[epoch][key] = 0
      current[epoch][key] += 1

    (handle, pathname) = tempfile.mkstemp(text=True)
    with open(pathname, 'w') as f:
      json.dump(current, f)
      f.write("\n")
    os.replace(pathname, cls.filename(epoch))
    os.close(handle)
    os.chown(
      cls.filename(epoch),
      int(os.environ.get('SUDO_UID', -1)),
      int(os.environ.get('SUDO_GID', -1)),
    )

  @classmethod
  def flush_logs(cls):
    for epoch in list(cls.log):
      if epoch < time.time() - TIME_RANGE:
        cls.flush_log(epoch)
        del cls.log[epoch]

  @classmethod
  def record_press(cls, event):
    t = TIME_RANGE * round(time.time() / TIME_RANGE)
    if t not in cls.log:
      cls.log[t] = []
    cls.log[t].append([event.scan_code] + sorted(list(cls.current)))

  @classmethod
  def key_pressed(cls, event):
    cls.record_press(event)
    cls.current[event.scan_code] = True

  @classmethod
  def key_released(cls, event):
    del cls.current[event.scan_code]

  @classmethod
  def hook(cls, event):
    if event.scan_code == 63:
      return # Fn key on Mac
    if event.event_type == keyboard.KEY_UP:
      cls.key_released(event)
    if event.event_type == keyboard.KEY_DOWN:
      cls.key_pressed(event)

class Mouse(Keyboard):
  log = {}
  last = None

  @classmethod
  def filename(cls, epoch):
    day = time.strftime("%Y-%m-%d", time.localtime(epoch))
    return f'{LOG_DIR}/mouse/{day}.json'

  @classmethod
  def on_click(cls, x, y, button, pressed):
    if not pressed:
      return
    b = None
    if button == mouse.Button.left:
      b = 'left'
    elif button == mouse.Button.right:
      b = 'right'
    elif button == mouse.Button.middle:
      b = 'middle'

    epoch = time.time()
    t = TIME_RANGE * round(epoch / TIME_RANGE)

    if cls.last and \
        cls.last['button'] == b and \
        cls.last['t'] >= epoch - 0.3:
      cls.log[TIME_RANGE * round(cls.last['t'] / TIME_RANGE)][-1][2] = f'double {b}'
      cls.last = None
    else:
      if t not in cls.log:
        cls.log[t] = []
      cls.log[t].append([round(x), round(y), b])
      cls.last = { 'button': b, 't': epoch }

keyboard.hook(Keyboard.hook)
listener = mouse.Listener(on_click = Mouse.on_click)
listener.start()

if __name__ == '__main__':
  if len(sys.argv) > 1 and sys.argv[1] == 'clean':
    shutil.rmtree(LOG_DIR)
    exit(0)
  while True:
    time.sleep(3)
    try:
      Keyboard.flush_logs()
      Mouse.flush_logs()
    except Exception as e:
      LOGGER.exception(e)
