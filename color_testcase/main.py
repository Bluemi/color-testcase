#!/usr/bin/env python3


import numpy as np
import matplotlib.pyplot as plt

from color_system import cs_hdtv
from black_bodies import planck


def main():
    print('main')
    cs = cs_hdtv
    lam = np.arange(380., 781., 5)
    spec = planck(lam, 6000)

    plt.plot(lam, spec)
    plt.show()

    print(np.max(spec))


if __name__ == '__main__':
    main()
