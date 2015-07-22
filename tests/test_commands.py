from botbuiltins.utils import *
from botbuiltins.xkcd import *
import pytest


@pytest.mark.parametrize("command, args, expected_result", [
    (command_alive, [], "Yes, I'm alive."),
    (command_xkcd, ["1000"], "http://xkcd.com/1000/"),
    (command_xkcdrandomnumber, [],
     "[4 // Chosen by fair dice roll. Guaranteed to be random.](http://xkcd.com/221/)"),
    (command_xkcd, [], "Not enough arguments.")
])
def test_commands(command, args, expected_result):
    assert command(None, None, args, None, None) == expected_result
