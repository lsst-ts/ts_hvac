# This file is part of ts_hvac.
#
# Developed for the Vera C. Rubin Observatory Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


__all__ = ["bar_to_pa", "determine_unit", "parse_limits", "psi_to_pa", "to_camel_case"]

import re
import typing

import astropy.units as u
from astropy.units import imperial, misc

# The default lower limit
DEFAULT_LOWER_LIMIT = -9999

# The default upper limit
DEFAULT_UPPER_LIMIT = 9999

# The molecular weight of CO2 (g/mol).
MOLECULAR_WEIGHT_CO2 = 44.009

# PPM to mg/m3 conversion factor.
PPM_CONVERSION_FACTOR = 0.0409


def bar_to_pa(value: float) -> float:
    """Convert a value in bar to a value in Pa.

    Parameters
    ----------
    value: `float`
        The value in bar.

    Returns
    -------
    float
        The value in Pa.
    """
    quantity_in_bar = value * misc.bar
    quantity_in_pa = quantity_in_bar.to(u.Pa)
    return quantity_in_pa.value


def psi_to_pa(value: float) -> float:
    """Convert a value in PSI to a value in Pa.

    Parameters
    ----------
    value: `float`
        The value in PSI.

    Returns
    -------
    float
        The value in Pa.
    """
    quantity_in_psi = value * imperial.psi
    quantity_in_pa = quantity_in_psi.to(u.Pa)
    return quantity_in_pa.value


def co2_ppm_to_mg_per_cubic_meter(value: float) -> float:
    """Convert a value in CO2 ppm to a value in mg/m3.

    Parameters
    ----------
    value: `float`
        The value in CO2 ppm.

    Returns
    -------
    float
        The value in mg/m3.
    """
    return value * MOLECULAR_WEIGHT_CO2 / PPM_CONVERSION_FACTOR


def to_camel_case(string: str, first_lower: bool = False) -> str:
    """Return a CamelCase or camelCase version of a snake_case str.

    Parameters
    ----------
    string: `str`
        The string to convert.
    first_lower: `bool`
        True for camelCase and False for CamelCase.

    Returns
    -------
    str
        The string in CamelCase or camelCase.
    """
    if first_lower:
        first, _, rest = string.partition("_")
    else:
        first, rest = ("", string)
    return first.lower() + "".join(part.capitalize() for part in rest.split("_"))


def determine_unit(unit_string: str) -> str:
    """Convert the provided unit string to a string representing the unit.

    Parameters
    ----------
    unit_string: `str`
        The unit as read from the input file.

    Returns
    -------
    unit: `str`
        A string representing the unit.
    """
    return {
        "-": "unitless",
        "": "unitless",
        "°C": "deg_C",
        "bar": "Pa",
        "%": "%",
        "Hz": "Hz",
        "hr": "h",
        "%RH": "%",
        "m3/h": "m3/h",
        "LPM": "l/min",
        "l/m": "l/min",
        "ppm": "mg/m3",
        "PSI": "Pa",
        "KW": "kW",
    }[unit_string.strip()]


def parse_limits(limits_string: str) -> typing.Tuple[int | float, int | float]:
    """Parse the string value of the limits column by comparing it to known
    regular expressions and extracting the minimum and maximum values.

    Parameters
    ----------
    limits_string: `str`
        The string containing the limits to parse.

    Returns
    -------
    lower_limit: `int` or `float`
        The lower limit
    upper_limit: `int` or `float`
        The upper limit

    Raises
    ------
    ValueError
        In case an unknown string pattern is found in the limits' column.

    """
    lower_limit: int | float = DEFAULT_LOWER_LIMIT
    upper_limit: int | float = DEFAULT_UPPER_LIMIT

    match = re.match(
        r"^(-?\d+)(/| a | ?% a |°C a | bar a |%RH a | LPM a | PSI a | KW a | ppm a )(-?\d+)"
        r"( ?%| ?°C| bar| hr|%RH| LPM| PSI| KW| ppm| Hz)?$",
        limits_string,
    )
    if match:
        lower_limit = float(match.group(1))
        upper_limit = float(match.group(3))
    elif re.match(r"^\d$", limits_string):
        lower_limit = 0
        upper_limit = 100
    elif limits_string == "1,2,3,4,5,6,7,8":
        lower_limit = 1
        upper_limit = 8
    elif limits_string == "1,2,3,4,5,6":
        lower_limit = 1
        upper_limit = 6
    elif limits_string == "1,2,3,4,5":
        lower_limit = 1
        upper_limit = 5
    elif limits_string == "1,2,3":
        lower_limit = 1
        upper_limit = 3
    elif limits_string in ["true o false", "-", "-1", ""]:
        # ignore because there really are no lower and upper limits
        pass
    else:
        raise ValueError(f"Couldn't match limits_string {limits_string!r}")

    # Convert non-standard units to standard ones.
    if "bar" in limits_string:
        lower_limit = round(bar_to_pa(lower_limit), 1)
        upper_limit = round(bar_to_pa(upper_limit), 1)
    if "PSI" in limits_string:
        lower_limit = round(psi_to_pa(lower_limit), 1)
        upper_limit = round(psi_to_pa(upper_limit), 1)

    return lower_limit, upper_limit
