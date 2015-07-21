import pytest

from botbuiltins.didyoumean import did_you_mean, unique_sorted


@pytest.mark.parametrize("given, expected", [
    ("listcommadns", "listcommands"),
    ("hepl", "help"),
    ("aliv", "alive"),
    ("bna", "ban"),
    ("unabn", "unban"),
    ("uct", "utc"),
    ("aaaaaa", None)
])
def test_didyoumean(given, expected):
    cmd_name_list = ["listcommands", "help", "alive", "ban", "unban", "utc"]
    assert did_you_mean(given, cmd_name_list) == expected


@pytest.mark.parametrize("given, expected", [
    ("acabcccbbcbc", "abc"),
    ("testing", "eginst")
])
def test_uniquesorted(given, expected):
    assert unique_sorted(given) == expected
