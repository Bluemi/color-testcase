import numpy as np
from color_testcase.color_system import cs_hdtv


def planck(lam, t):
    """
    Returns the spectral radiance of a black body at temperature t.

    Returns the spectral radiance, B(lam, t), in W.sr-1.m-2 of a black body
    at temperature t (in K) at a wavelength lam (in nm), using Planck's law.
    """
    # define constants h, c, k to get rid of scipy dependency.
    # from scipy.constants import h, c, k
    h = 6.62607015e-34
    c = 299792458.0
    k = 1.380649e-23

    lam_m = lam / 1.e9
    fac = h * c / lam_m / k / t
    b = 2*h*c**2/lam_m**5 / (np.exp(fac) - 1)
    return b


def main():
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle

    cs = cs_hdtv

    fig, ax = plt.subplots()

    # The grid of visible wavelengths corresponding to the grid of colour-matching
    # functions used by the ColourSystem instance.
    lam = np.arange(380., 781., 5)

    for i in range(24):
        # t = 500 to 12000 K
        t = 500*i + 500

        # Calculate the black body spectrum and the HTML hex RGB colour string
        # it looks like
        spec = planck(lam, t)
        html_rgb = cs.spec_to_rgb(spec, out_fmt='html')

        # Place and label a circle with the colour of a black body at temperature t
        x, y = i % 6, -(i // 6)
        circle = Circle(xy=(x, y*1.2), radius=0.4, fc=html_rgb)
        ax.add_patch(circle)
        ax.annotate('{:4d} K'.format(t), xy=(x, y*1.2-0.5), va='center',
                    ha='center', color=html_rgb)

    # Set the limits and background colour; remove the ticks
    ax.set_xlim(-0.5, 5.5)
    ax.set_ylim(-4.35, 0.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_facecolor('k')
    # Make sure our circles are circular!
    ax.set_aspect("equal")
    plt.show()


if __name__ == '__main__':
    main()
