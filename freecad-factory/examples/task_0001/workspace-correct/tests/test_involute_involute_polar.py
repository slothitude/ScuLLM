"""Tests for genInvolutePolar() in Mod/PartDesign/fcgear/involute.py.

Definition under test: the involute polar angle of radius R on a base circle
of radius Rb is

    t(R) = sqrt(R**2 - Rb**2) / Rb - acos(Rb / R)

so that an involute generated with parameter t is located at exactly that
angle for radius R(t).
"""

import math
import os
import sys

import pytest

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), os.pardir, "Mod", "PartDesign", "fcgear")
)

from involute import genInvolutePolar  # noqa: E402


def test_angle_is_zero_at_base_circle():
    """At the base circle the involute has swept no angle yet."""
    assert genInvolutePolar(10.0, 10.0) == pytest.approx(0.0, abs=1e-12)


def test_known_angle_r10_r20():
    """Closed-form check, derived independently of the implementation.

    The involute point at parameter t is x=Rb*(cos t + t*sin t),
    y=Rb*(sin t - t*cos t); its radius is R = Rb*sqrt(1 + t**2) and its
    polar angle is t - atan(t).  For Rb=10, R=20 => t=sqrt(3), so the
    swept angle must be sqrt(3) - atan(sqrt(3)) = 0.6848532563723449.
    """
    t = math.sqrt(3.0)
    expected = t - math.atan(t)
    assert genInvolutePolar(10.0, 20.0) == pytest.approx(expected, abs=1e-12)


def test_parametric_roundtrip():
    """The involute point at parameter t sits at polar angle t - atan(t).

    x(t) = Rb*(cos t + t*sin t), y(t) = Rb*(sin t - t*cos t),
    R = hypot(x, y)  =>  genInvolutePolar(Rb, R) == t - atan(t).
    """
    Rb = 10.0
    for t in (0.2, 0.7, 1.4):
        x = Rb * (math.cos(t) + t * math.sin(t))
        y = Rb * (math.sin(t) - t * math.cos(t))
        R = math.hypot(x, y)
        assert genInvolutePolar(Rb, R) == pytest.approx(t - math.atan(t), abs=1e-9)
