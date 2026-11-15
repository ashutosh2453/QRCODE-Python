from urllib.parse import parse_qs, urlparse

import pytest
from PIL import Image

from qr_generator import QRInputError, build_upi_uri, main, make_qr, normalise_amount, save_qr, validate_vpa


@pytest.mark.parametrize("vpa", ["asha.k@okhdfcbank", "9876543210@ybl", "shop_01-x@paytm"])
def test_valid_vpas(vpa):
    assert validate_vpa(f"  {vpa} ") == vpa


@pytest.mark.parametrize("vpa", ["", "no-at-sign", "a@", "@bank", "x y@okaxis", "a@b", "name@1bank"])
def test_invalid_vpas(vpa):
    with pytest.raises(QRInputError):
        validate_vpa(vpa)


def test_upi_uri_is_encoded_and_has_no_merchant_code():
    uri = build_upi_uri("asha@okhdfcbank", "Asha Kumar & Co", "250", "Dinner split")
    parsed = urlparse(uri)
    qs = parse_qs(parsed.query)
    assert parsed.scheme == "upi" and parsed.netloc == "pay"
    assert qs == {"pa": ["asha@okhdfcbank"], "pn": ["Asha Kumar & Co"], "am": ["250.00"],
                  "cu": ["INR"], "tn": ["Dinner split"]}
    assert "mc=" not in uri


def test_upi_uri_without_amount():
    assert "am=" not in build_upi_uri("asha@okhdfcbank", "Asha")


@pytest.mark.parametrize("raw,expected", [("10", "10.00"), ("99.999", "100.00"), ("0.5", "0.50"), (None, None), ("", None)])
def test_amount_normalisation(raw, expected):
    assert normalise_amount(raw) == expected


@pytest.mark.parametrize("raw", ["abc", "0", "-5", "100000.01", "nan", "inf"])
def test_invalid_amounts(raw):
    with pytest.raises(QRInputError):
        normalise_amount(raw)


def test_empty_name_rejected():
    with pytest.raises(QRInputError):
        build_upi_uri("asha@okhdfcbank", "   ")


def test_box_size_and_border_change_image_size():
    small = make_qr("hello", box_size=2, border=0)
    big = make_qr("hello", box_size=4, border=4)
    assert big.size[0] == 2 * small.size[0] + 2 * 4 * 4


@pytest.mark.parametrize("kwargs", [{"box_size": 0}, {"border": 21}, {"error_correction": "Z"}])
def test_make_qr_rejects_bad_options(kwargs):
    with pytest.raises(QRInputError):
        make_qr("hello", **kwargs)


def test_save_qr_forces_image_extension(tmp_path):
    path = save_qr("hello", tmp_path / "nested" / "code.txt")
    assert path.suffix == ".png" and Image.open(path).format == "PNG"


def test_cli_text_and_upi(tmp_path, capsys):
    assert main(["text", "https://example.com", "-o", str(tmp_path / "t.png")]) == 0
    assert main(["upi", "--vpa", "asha@okhdfcbank", "--name", "Asha", "--amount", "50", "-o", str(tmp_path / "u.png")]) == 0
    assert "am=50.00" in capsys.readouterr().out
    assert main(["upi", "--vpa", "bad", "--name", "Asha", "-o", str(tmp_path / "x.png")]) == 2
    assert not (tmp_path / "x.png").exists()
