import math
import pandas as pd

field       = 800 
wave        =  50
grid_count  = 300
grid_unit   = field / grid_count
grid_offset = grid_count / 2 * grid_unit
x0          = -grid_offset
y0          = -grid_offset
wmax        = grid_unit * 0.8
hmax        = grid_unit * 0.8
wmin        = grid_unit * 0.1
hmin        = grid_unit * 0.1
wrng        = wmax - wmin
hrng        = hmax - hmin
result      = []

for xi in range(grid_count):
    for yi in range(grid_count):
        x    = round(x0 + grid_unit * xi, 1)
        y    = round(y0 + grid_unit * yi, 1)
        dist = (x ** 2 + y ** 2) ** (0.5)
        rot  = round((0 if x == 0 else (math.atan(y/x) / math.pi * 180)) + 90, 0)
        wv   = round((1 - min([(dist % wave), wave - (dist % wave)])/wave), 1)
        w    = round(math.sin(wv * math.pi) * wrng + wmin, 1) 
        h    = round(math.sin(wv * math.pi) * hrng + hmin, 1) 

        result.append({
            "x" :     x,
            "y" :     y,
            "width":  w,
            "height": h,
            "rotate": rot,
        })

df = pd.DataFrame(result)
print(df)
df.to_csv("lens.csv")