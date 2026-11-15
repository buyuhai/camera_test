import pytest

from hough_gui.core.params import HoughParams


def test_default_values_are_valid():
    params = HoughParams()
    assert (
        params.dp,
        params.min_dist,
        params.param1,
        params.param2,
        params.min_radius,
        params.max_radius,
    ) == (1.0, 50, 100, 30, 0, 0)
    assert params.validate() == []


@pytest.mark.parametrize(
    "overrides",
    [
        {"dp": 0},
        {"dp": -1.0},
        {"min_dist": 0},
        {"param1": 0},
        {"param2": -5},
        {"min_radius": -1},
        {"max_radius": -1},
        {"min_radius": 50, "max_radius": 30},
    ],
)
def test_invalid_values_are_reported(overrides):
    assert HoughParams(**overrides).validate()


def test_nonzero_max_radius_above_min_radius_is_valid():
    assert HoughParams(min_radius=20, max_radius=200).validate() == []
