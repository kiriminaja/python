from kiriminaja.utils.volumetric import Dimensions, VolumetricItem, calculate


def test_empty():
    assert calculate([]) == Dimensions(0, 0, 0)


def test_single_item_dict():
    out = calculate([{"qty": 1, "length": 10, "width": 5, "height": 3}])
    assert out == Dimensions(10, 5, 3)


def test_single_item_dataclass():
    out = calculate([VolumetricItem(qty=1, length=10, width=5, height=3)])
    assert out == Dimensions(10, 5, 3)


def test_vertical_wins():
    out = calculate([VolumetricItem(qty=2, length=10, width=10, height=2)])
    assert out == Dimensions(10, 10, 4)


def test_horizontal_wins():
    out = calculate([
        VolumetricItem(qty=5, length=2, width=10, height=10),
        VolumetricItem(qty=1, length=10, width=1, height=1),
    ])
    assert out == Dimensions(20, 10, 10)


def test_side_wins():
    out = calculate([
        VolumetricItem(qty=5, length=10, width=2, height=10),
        VolumetricItem(qty=1, length=1, width=10, height=1),
    ])
    assert out == Dimensions(10, 20, 10)


def test_qty_zero_treated_as_one():
    out = calculate([VolumetricItem(qty=0, length=10, width=5, height=3)])
    assert out == Dimensions(10, 5, 3)
