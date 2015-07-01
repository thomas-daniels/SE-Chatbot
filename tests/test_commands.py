from builtins.utils import *
import Commands
import pytest


@pytest.mark.parametrize("command, args, expected_result, arg_count", [
    (command_alive, [], "Yes, I'm alive.", 5),
    (Commands.command_xkcd, ["1000"], "http://xkcd.com/1000/", 3),
    (Commands.command_xkcdrandomnumber, [],
     "[4 // Chosen by fair dice roll. Guaranteed to be random.](http://xkcd.com/221/)", 3),
    (Commands.command_xkcd, [], "Not enough arguments.", 3)
])
def test_commands(command, args, expected_result, arg_count):
    if arg_count == 5:
        assert command(None, None, args, None, None) == expected_result
    else:
        assert command(args, None, None) == expected_result