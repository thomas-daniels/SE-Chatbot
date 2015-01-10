import Commands
import pytest


@pytest.mark.parametrize("command, args, expected_result", [
    (Commands.command_alive, [], "Yes, I'm alive."),
    (Commands.command_xkcd, ["1000"], "http://xkcd.com/1000/"),
    (Commands.command_xkcdrandomnumber, [],
     "[4 // Chosen by fair dice roll. Guaranteed to be random.](http://xkcd.com/221/)"),
    (Commands.command_xkcd, [], "Not enough arguments.")
])
def test_commands(command, args, expected_result):
    assert command(args, None, None) == expected_result