#!/usr/bin/env python2.7

import dish
import time

start = time.time()
d = dish.Dish()
d.home()

delta = time.time() - start
print delta / 60.0
