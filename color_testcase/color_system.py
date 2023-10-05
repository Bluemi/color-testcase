"""
Taken from: https://scipython.com/blog/converting-a-spectrum-to-a-colour/
"""
import numpy as np

CIE_CMF = np.array([[0.0014, 0., 0.0065],
                    [0.0022, 0.0001, 0.0105],
                    [0.0042, 0.0001, 0.0201],
                    [0.0076, 0.0002, 0.0362],
                    [0.0143, 0.0004, 0.0679],
                    [0.0232, 0.0006, 0.1102],
                    [0.0435, 0.0012, 0.2074],
                    [0.0776, 0.0022, 0.3713],
                    [0.1344, 0.004, 0.6456],
                    [0.2148, 0.0073, 1.0391],
                    [0.2839, 0.0116, 1.3856],
                    [0.3285, 0.0168, 1.623],
                    [0.3483, 0.023, 1.7471],
                    [0.3481, 0.0298, 1.7826],
                    [0.3362, 0.038, 1.7721],
                    [0.3187, 0.048, 1.7441],
                    [0.2908, 0.06, 1.6692],
                    [0.2511, 0.0739, 1.5281],
                    [0.1954, 0.091, 1.2876],
                    [0.1421, 0.1126, 1.0419],
                    [0.0956, 0.139, 0.813],
                    [0.058, 0.1693, 0.6162],
                    [0.032, 0.208, 0.4652],
                    [0.0147, 0.2586, 0.3533],
                    [0.0049, 0.323, 0.272],
                    [0.0024, 0.4073, 0.2123],
                    [0.0093, 0.503, 0.1582],
                    [0.0291, 0.6082, 0.1117],
                    [0.0633, 0.71, 0.0782],
                    [0.1096, 0.7932, 0.0573],
                    [0.1655, 0.862, 0.0422],
                    [0.2257, 0.9149, 0.0298],
                    [0.2904, 0.954, 0.0203],
                    [0.3597, 0.9803, 0.0134],
                    [0.4334, 0.995, 0.0087],
                    [0.5121, 1., 0.0057],
                    [0.5945, 0.995, 0.0039],
                    [0.6784, 0.9786, 0.0027],
                    [0.7621, 0.952, 0.0021],
                    [0.8425, 0.9154, 0.0018],
                    [0.9163, 0.87, 0.0017],
                    [0.9786, 0.8163, 0.0014],
                    [1.0263, 0.757, 0.0011],
                    [1.0567, 0.6949, 0.001],
                    [1.0622, 0.631, 0.0008],
                    [1.0456, 0.5668, 0.0006],
                    [1.0026, 0.503, 0.0003],
                    [0.9384, 0.4412, 0.0002],
                    [0.8544, 0.381, 0.0002],
                    [0.7514, 0.321, 0.0001],
                    [0.6424, 0.265, 0.],
                    [0.5419, 0.217, 0.],
                    [0.4479, 0.175, 0.],
                    [0.3608, 0.1382, 0.],
                    [0.2835, 0.107, 0.],
                    [0.2187, 0.0816, 0.],
                    [0.1649, 0.061, 0.],
                    [0.1212, 0.0446, 0.],
                    [0.0874, 0.032, 0.],
                    [0.0636, 0.0232, 0.],
                    [0.0468, 0.017, 0.],
                    [0.0329, 0.0119, 0.],
                    [0.0227, 0.0082, 0.],
                    [0.0158, 0.0057, 0.],
                    [0.0114, 0.0041, 0.],
                    [0.0081, 0.0029, 0.],
                    [0.0058, 0.0021, 0.],
                    [0.0041, 0.0015, 0.],
                    [0.0029, 0.001, 0.],
                    [0.002, 0.0007, 0.],
                    [0.0014, 0.0005, 0.],
                    [0.001, 0.0004, 0.],
                    [0.0007, 0.0002, 0.],
                    [0.0005, 0.0002, 0.],
                    [0.0003, 0.0001, 0.],
                    [0.0002, 0.0001, 0.],
                    [0.0002, 0.0001, 0.],
                    [0.0001, 0., 0.],
                    [0.0001, 0., 0.],
                    [0.0001, 0., 0.],
                    [0., 0., 0.]])


def xyz_from_xy(x, y):
    """Return the vector (x, y, 1-x-y)."""
    return np.array((x, y, 1 - x - y))


def rgb_to_hex(rgb):
    """Convert from fractional rgb values to HTML-style hex string."""
    hex_rgb = (255 * rgb).astype(int)
    return '#{:02x}{:02x}{:02x}'.format(*hex_rgb)


class ColourSystem:
    """A class representing a colour system.

    A colour system defined by the CIE x, y and z=1-x-y coordinates of
    its three primary illuminants and its "white point".

    TODO: Implement gamma correction
    """
    # The CIE colour matching function for 380 - 780 nm in 5 nm intervals
    cmf = CIE_CMF

    def __init__(self, red, green, blue, white):
        """
        Initialise the ColourSystem object.
        Pass vectors (ie NumPy arrays of shape (3,)) for each of the
        red, green, blue  chromaticities and the white illuminant
        defining the colour system.
        """
        # Chromaticities
        self.red, self.green, self.blue = red, green, blue
        self.white = white
        # The chromaticity matrix (rgb -> xyz) and its inverse
        self.M = np.vstack((self.red, self.green, self.blue)).T
        self.MI = np.linalg.inv(self.M)
        # White scaling array
        self.wscale = self.MI.dot(self.white)
        # xyz -> rgb transformation matrix
        self.T = self.MI / self.wscale[:, np.newaxis]

    def xyz_to_rgb(self, xyz, out_fmt=None, normalize=False):
        """
        Transform from xyz to rgb representation of colour.

        The output rgb components are normalized on their maximum
        value. If xyz is out the rgb gamut, it is desaturated until it
        comes into gamut.

        By default, fractional rgb components are returned; if
        out_fmt='html', the HTML hex string '#rrggbb' is returned.
        """
        rgb = self.T.dot(xyz)
        if np.any(rgb < 0):
            # We're not in the RGB gamut: approximate by desaturating
            w = - np.min(rgb)
            rgb += w
        if normalize and not np.all(rgb == 0):
            # Normalize the rgb vector
            rgb /= np.max(rgb)

        if out_fmt == 'html':
            return rgb_to_hex(rgb)
        return rgb

    def spec_to_xyz(self, spec, normalize):
        """
        Convert a spectrum to a xyz point.

        The spectrum must be on the same grid of points as the colour-matching
        function, self.cmf: 380-780 nm in 5 nm steps.
        """
        xyz = np.sum(spec[:, np.newaxis] * self.cmf, axis=0)
        den = 1.0
        if normalize:
            den = np.sum(xyz)
        if den == 0.:
            return xyz
        return xyz / den

    def spec_to_rgb(self, spec, out_fmt=None, normalize=False):
        """Convert a spectrum to a rgb value."""
        xyz = self.spec_to_xyz(spec, normalize)
        return self.xyz_to_rgb(xyz, out_fmt, normalize=normalize)


illuminant_D65 = xyz_from_xy(0.3127, 0.3291)
cs_hdtv = ColourSystem(red=xyz_from_xy(0.67, 0.33),
                       green=xyz_from_xy(0.21, 0.71),
                       blue=xyz_from_xy(0.15, 0.06),
                       white=illuminant_D65)

cs_smpte = ColourSystem(red=xyz_from_xy(0.63, 0.34),
                        green=xyz_from_xy(0.31, 0.595),
                        blue=xyz_from_xy(0.155, 0.070),
                        white=illuminant_D65)

cs_srgb = ColourSystem(red=xyz_from_xy(0.64, 0.33),
                       green=xyz_from_xy(0.30, 0.60),
                       blue=xyz_from_xy(0.15, 0.06),
                       white=illuminant_D65)
