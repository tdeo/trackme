import json
import os

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

WIDTH = 50

x_bounds = [0, 0]
y_bounds = [0, 0]

DIR = f'{os.environ.get("HOME")}/.trackme/logs/mouse'

count = {}

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

print(x_bounds, y_bounds, count)
