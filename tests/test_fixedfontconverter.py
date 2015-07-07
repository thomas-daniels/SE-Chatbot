from fixedfont import fixed_font_to_normal, is_fixed_font
import os


def test_fixedfontconverter():
    inp = "def test():\r\n        print(\"Test\")\r\n    test()"
    expected = """def test():{0}    print("Test"){0}test()"""\
        .format(os.linesep)
    assert fixed_font_to_normal(inp) == expected


def test_isfixedfont():
    assert is_fixed_font(
        "def test():\r\n        print(\"Test\")\r\n    test()"
    )
