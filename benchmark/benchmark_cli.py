"""
CLI for making benchmark tests.

"""
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
from sys import version
from textwrap import dedent

from benchmark import project_name

python_ver = version.split()[0]

arg_parser = ArgumentParser(
    prog=f"python3 {Path(__file__).name}",
    description=f"Make benchmark tests for {project_name.replace(' ', '_')} package",
    epilog=f"v0.1.0, python {python_ver}",
    formatter_class=RawTextHelpFormatter,
)

arg_parser.add_argument(
    "--size",
    help=dedent(
        """\
    make tests for different size of sets
    """
    ),
    metavar="10 100",
    type=int,
    nargs="+",
    required=True,
)

arg_parser.add_argument(
    "--log",
    help=dedent(
        """\
    name of the log file to store results
    """
    ),
    metavar="filename",
    type=str,
    required=False,
)

arg_parser.add_argument(
    "--img",
    help=dedent(
        """\
    name of the image file to store results
    """
    ),
    metavar="filename",
    type=str,
    required=False,
)

arg_parser.add_argument(
    "--print",
    help=dedent(
        """\
    display execution time of each test on the screen
    """
    ),
    action="store_true",
    required=False,
)

arg_parser.add_argument(
    "--show",
    help=dedent(
        """\
    display image with results on the screen
    """
    ),
    action="store_true",
    required=False,
)

args = arg_parser.parse_args()
