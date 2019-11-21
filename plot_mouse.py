import json
import os

WIDTH = 20

x_bounds = [0, 0]
y_bounds = [0, 0]

DIR = f'{os.environ.get("HOME")}/.trackme/logs/mouse'

count = {}
MAX_ZONE = 0
total = 0

for f in os.listdir(DIR):
  if not os.path.isfile(os.path.join(DIR, f)):
    continue
  with open(os.path.join(DIR, f)) as file:
    content = json.load(file)

  for ts in content:
    for pos in content[ts]:
      line = pos.split(',')
      x = int(line[0]) // WIDTH
      y = int(line[1]) // WIDTH
      x_bounds = [min(x, x_bounds[0]), max(x, x_bounds[1])]
      y_bounds = [min(y, y_bounds[0]), max(y, y_bounds[1])]

      if x not in count:
        count[x] = {}
      if y not in count[x]:
        count[x][y] = 0
      count[x][y] += content[ts][pos]
      MAX_ZONE = max(MAX_ZONE, count[x][y])
      total += content[ts][pos]

svg = f'''
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
  width="{WIDTH / 2 * (x_bounds[1] - x_bounds[0] + 3)}" height="{WIDTH / 2 * (y_bounds[1] - y_bounds[0] + 3)}"
  viewBox="{x_bounds[0] - 1} {y_bounds[0] - 1} {x_bounds[1] - x_bounds[0] + 3} {y_bounds[1] - y_bounds[0] + 3}"
  version="1.1">
    <rect width="{x_bounds[1] - x_bounds[0] + 3}" height="{y_bounds[1] - y_bounds[0] + 3}"
      x="{x_bounds[0] - 1}" y="{y_bounds[0] - 1}" stroke="grey" stroke-width="1" fill="none" />
    <rect width="{x_bounds[1] - x_bounds[0] + 3}" height="0.2"
      x="{x_bounds[0] - 1}" y="-0.1" stroke="none" fill="grey" />
    <g>'''

for x in count:
  for y in count[x]:
    svg += f'''
      <rect width="{1}" height="{1}" x="{x}" y="{y}" stroke="none" fill="red" fill-opacity="{count[x][y] / MAX_ZONE}" />'''

svg += '\n</g></svg>'

print(svg)
