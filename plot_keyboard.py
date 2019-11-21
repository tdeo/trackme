import json
import os

import keyboard

DIR = f'{os.environ.get("HOME")}/.trackme/logs/keyboard'

count = {}
MAX_KEY = 0
total = 0

for f in os.listdir(DIR):
  if not os.path.isfile(os.path.join(DIR, f)):
    continue
  with open(os.path.join(DIR, f)) as file:
    content = json.load(file)

  for ts in content:
    for keys in content[ts]:
      key = keys.split(',')[0]

      if key not in count:
        count[key] = 0
      count[key] += content[ts][keys]
      MAX_KEY = max(MAX_KEY, count[key])
      total += content[ts][keys]

K = 10
w = K * len(count)

svg = f'''
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
  width="{w + 40}" height="{w + 10}"
  viewBox="-15 -5 {w + 40} {w + 10}"
  version="1.1">
    <rect width="{w + 40}" height="{w + 10}"
      x="{-15}" y="{-5}" stroke="grey" stroke-width="1" fill="none" />
    <g>'''

i = 0
for k in reversed(sorted(count, key=count.get)):
  svg += f'''
    <rect height="{K - 2}" width="{w * count[k] / MAX_KEY}" y="{K * i + 1}" x="{0}" stroke="#777" fill="#dff" />
    <text y="{K * i + 8}" x="-14" style="font-size: 7px">{keyboard._os_keyboard.name_from_scancode(int(k))}</text>
    <text y="{K * i + 8}" x="{w * count[k] / MAX_KEY + 3}" style="font-size: 7px">{count[k]}</text> '''
  i += 1

svg += '\n</g></svg>'

print(svg)
