"""
CLI for making benchmark tests.

"""
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
from textwrap import dedent

import matplotlib.pyplot as plt  # type: ignore

from benchmark import project_name
from benchmark.testlib import (
    execute_data_frame,
    execute_object_query,
    plot_results,
    python_ver,
    setup_test_objects,
    test_filtering,
    tested_version,
)

arg_parser = ArgumentParser(
    prog=f"python3 {Path(__file__).name}",
    description=f"Make benchmark tests for {project_name.replace(' ', '_')} package",
    epilog=f"v0.1.1, python {python_ver}",
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
args.size = sorted(args.size)

oq_performance = []
df_performance = []
results = "# NoRows ObjectQuery DataFrame\n"
fig = None

for size in args.size:
    oq_perf = test_filtering(size, setup_test_objects, execute_object_query)
    df_perf = test_filtering(size, setup_test_objects, execute_data_frame)
    oq_performance.append(oq_perf)
    df_performance.append(df_perf)

if args.print or (args.log is not None):
    for size, oq_perf, df_perf in zip(args.size, oq_performance, df_performance):
        results += f"{size} {oq_perf} {df_perf}\n"

if args.print:
    print(results, end="")

if args.log is not None:
    with open(args.log, "w") as fd:
        fd.write(results)

if args.show or (args.img is not None):
    fig = plot_results(
        args.size,
        f"{project_name.title().replace(' ','')} -- performance of filtering",
        tested_version(),
        ObjectQuery=oq_performance,
        DataFrame=df_performance,
    )
    if args.img is not None:
        fig.savefig(args.img, bbox_inches="tight", pad_inches=0.2, dpi=120)

if args.show:
    plt.show()
