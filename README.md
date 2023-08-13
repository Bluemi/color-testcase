# Spectrum Visualization
Small utility program to visualize the relation between spectrum and color.
Transition from spectrum to color is taken from the [Blogpost "Converting a spectrum to a colour"](https://scipython.com/blog/converting-a-spectrum-to-a-colour/).

## Usage
The left side shows a spectrum from 380 nm to 781 nm wave length with a 5 nm step.

The right side shows the resulting color from this spectrum.

### Changing the spectrum
To change the spectrum just click on it and move the cursor around.

There are also some predefined spectrums that can be set by pressing the following keys:
- Number keys `1`, ..., `9`, `0`: Set a spectrum that is emitted by a [blackbody](https://en.wikipedia.org/wiki/Black-body_radiation) at temperature `key` * 1000 Kelvin (10000 Kelvin for key `0`).
- `r`, `g`, `b`: Set a spectrum with color red, green or blue.
- `c`, `m`, `y`, `k`: Set a spectrum with color cyan, magenta, yellow or black.
- `+`, `-`: Change the position of the spectrum.

### Using filters
The shown spectrum can be filtered by a filter. To activate the filter press `f`.

All keys that modify the spectrum can also modify the filter in the same way by holding `shift` at the same time.

### Normalizing colors
By default, the color on the right side and the colors of the spectrum are not normalized.
To toggle the normalization of the spectrum press `N`. To toggle the normalization of the color on the right side press `n`.

### Quit
Pressing `Esc` will terminate the application.
