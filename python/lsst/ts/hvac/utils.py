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


__all__ = ["bar_to_pa", "psi_to_pa", "to_camel_case"]

import astropy.units as u
from astropy.units import imperial, misc

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
