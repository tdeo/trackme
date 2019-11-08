import json
import logging
import time
import os
import tempfile

import keyboard
import mouse

TIME_RANGE = 3 # time to group logs, in seconds

LOGGER = logging.getLogger('trackme')
LOGGER.setLevel(logging.DEBUG)

LOG_DIR = f'{os.environ.get("HOME")}/.trackme/logs'
os.makedirs(f'{LOG_DIR}/keyboard', exist_ok=True)
os.makedirs(f'{LOG_DIR}/mouse', exist_ok=True)

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
      key = ','.join([str(i) for i in e])
      if key not in current[epoch]:
        current[epoch][key] = 0
      current[epoch][key] += 1

    (_, pathname) = tempfile.mkstemp(text=True)
    with open(pathname, 'w') as f:
      json.dump(current, f)
      f.write("\n")
    os.replace(pathname, cls.filename(epoch))

  @classmethod
  def flush_logs(cls):
    for epoch in list(cls.log):
      if epoch < time.time() - TIME_RANGE:
        cls.flush_log(epoch)
        del cls.log[epoch]

  @classmethod
  def record_event(cls):
    t = TIME_RANGE * round(time.time() / TIME_RANGE) # ts at start of minute
    if t not in cls.log:
      cls.log[t] = []
    cls.log[t].append(sorted(list(cls.current)))

  @classmethod
  def key_pressed(cls, event):
    cls.pressSinceRelease = True
    cls.current[event.scan_code] = True

  @classmethod
  def key_released(cls, event):
    if cls.pressSinceRelease:
      cls.record_event()
    del cls.current[event.scan_code]
    cls.pressSinceRelease = False

  @classmethod
  def hook(cls, event):
    if event.event_type == keyboard.KEY_UP:
      cls.key_released(event)
    if (event.event_type == keyboard.KEY_DOWN) and (event.scan_code != 63): # fn key
      cls.key_pressed(event)

class Mouse(Keyboard):
  @classmethod

keyboard.hook(Keyboard.hook)

if __name__ == '__main__':
  while True:
    time.sleep(3)
    try:
      Keyboard.flush_logs()
    except Exception as e:
      LOGGER.exception(e)
