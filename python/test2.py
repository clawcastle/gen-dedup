import numpy as np
import math

uniques = []
count = 0

max16 = math.pow(2, 16)
max8 = math.pow(2, 8)

for _ in range(10000):
    base = np.random.normal(max16 // 2, 5000, size=1).astype(np.uint16).tobytes()
    deviation = np.random.normal(max8 // 2, 30, size=1).astype(np.uint8).tobytes()
    if base not in uniques:
        uniques.append(base)
    else:
        count += 1

print(count)
print(len(uniques))

uniques = []
count = 0

for _ in range(10000):
    values = np.random.normal(128, 30, size=3)
    as_bytes = values.astype(np.uint8).tobytes()

    if as_bytes[0:2] not in uniques:
        uniques.append(as_bytes[0:2])
    else:
        count += 1

print(count)
print(len(uniques))