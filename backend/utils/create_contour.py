import os
import sys
import scipy
import numpy as np
from scipy import signal

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from data_reader.data_reader import DataReader

dr = DataReader()
shot_df = dr.read_shot(index="shots-20210327141514-data", shot_number=5)

mask = np.array(
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1,],
        [1, 1, 1, 1, 1, 1, 1, 1, 1,],
        [1, 1, 1, 1, 1, 1, 1, 1, 1,],
        [1, 1, 1, 1, 1, 1, 1, 1, 1,],
        [1, 1, 1, 1, 1, 1, 1, 1, 1,],
        [1, 1, 1, 1, 1, 1, 1, 1, 1,],
        [1, 1, 1, 1, 1, 1, 1, 1, 1,],
        [1, 1, 1, 1, 1, 1, 1, 1, 1,],
        [1, 1, 1, 1, 1, 1, 1, 1, 1,],
    ]
)
mask = mask / 21
print(mask)

h_contor_array = []
# 80枚の図
for t in range(1000, 5000, 50):
    z = np.zeros((64, 64), dtype="float64")
    z[20, 20] = shot_df.load01[t]
    z[20, 40] = shot_df.load02[t]
    z[40, 20] = shot_df.load03[t]
    z[40, 40] = shot_df.load04[t]

    _a = scipy.signal.correlate2d(z, mask, mode="same", boundary="wrap")
    _a = scipy.signal.correlate2d(_a, mask, mode="same", boundary="wrap")
    _a = scipy.signal.correlate2d(_a, mask, mode="same", boundary="wrap")
    _a = scipy.signal.correlate2d(_a, mask, mode="same", boundary="wrap")
    _a = scipy.signal.correlate2d(_a, mask, mode="same", boundary="wrap")
    _a = scipy.signal.correlate2d(_a, mask, mode="same", boundary="wrap")
    _a = scipy.signal.correlate2d(_a, mask, mode="same", boundary="wrap")
    #     _a = scipy.signal.correlate2d(_a, mask, mode="same", boundary="wrap")
    #     _a = scipy.signal.correlate2d(_a, mask, mode="same", boundary="wrap")
    #     _a = scipy.signal.correlate2d(_a, mask, mode="same", boundary="wrap")
    h_contor_array.append(_a)

h_contor_array = np.array(h_contor_array)
