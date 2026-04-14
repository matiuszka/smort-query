"""
CLI for making benchmark tests.

Usage examples:
    # Run all operations with all engines at default sizes
    python -m benchmark.benchmark_cli --size 100 1000 10000 --print

    # Run only filter and sort with specific engines
    python -m benchmark.benchmark_cli --size 100 1000 --operations filter sort \
        --engines ObjectQuery pandas polars --print

    # Save chart to file
    python -m benchmark.benchmark_cli --size 100 500 1000 5000 10000 --img results.png

    # Full run with all outputs
    python -m benchmark.benchmark_cli --size 100 500 1000 5000 10000 50000 \
        --print --log results.txt --img results.png --show
"""

from __future__ import annotations

from argparse import ArgumentParser, RawTextHelpFormatter
from textwrap import dedent

import matplotlib.pyplot as plt  # type: ignore

from benchmark import project_name
from benchmark.engines import ALL_ENGINES, ENGINE_MAP, OPERATION_NAMES, Engine
from benchmark.testlib import (
    generate_humans,
    plot_results,
    python_ver,
    run_benchmark,
    tested_version,
)

# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

arg_parser = ArgumentParser(
    prog="python -m benchmark.benchmark_cli",
    description=f"Benchmark tests for {project_name.replace(' ', '_')} package.\n\n"
    f"Compares ObjectQuery against pandas, polars, list comprehension,\n"
    f"filter()+lambda, SQLite in-memory, and DuckDB in-memory.",
    epilog=f"v0.2.0, python {python_ver}",
    formatter_class=RawTextHelpFormatter,
)

arg_parser.add_argument(
    "--size",
    help="dataset sizes to benchmark (e.g. 100 1000 10000)",
    metavar="N",
    type=int,
    nargs="+",
    required=True,
)

arg_parser.add_argument(
    "--operations",
    help=dedent(
        f"operations to benchmark (default: all)\nchoices: {', '.join(OPERATION_NAMES)}"
    ),
    metavar="OP",
    type=str,
    nargs="+",
    choices=OPERATION_NAMES,
    default=OPERATION_NAMES,
)

arg_parser.add_argument(
    "--engines",
    help=dedent(
        f"engines to compare (default: all)\nchoices: {', '.join(ENGINE_MAP.keys())}"
    ),
    metavar="ENGINE",
    type=str,
    nargs="+",
    default=None,
)

arg_parser.add_argument(
    "--log",
    help="save results to a text log file",
    metavar="FILENAME",
    type=str,
    required=False,
)

arg_parser.add_argument(
    "--img",
    help="save chart image to file",
    metavar="FILENAME",
    type=str,
    required=False,
)

arg_parser.add_argument(
    "--print",
    help="display results on the screen",
    action="store_true",
    required=False,
)

arg_parser.add_argument(
    "--show",
    help="display chart window",
    action="store_true",
    required=False,
)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _resolve_engines(engine_names: list[str] | None) -> list[Engine]:
    """Resolve engine names to Engine instances."""
    if engine_names is None:
        return list(ALL_ENGINES)
    engines: list[Engine] = []
    for name in engine_names:
        if name not in ENGINE_MAP:
            raise SystemExit(
                f"Unknown engine: {name!r}. Available: {', '.join(ENGINE_MAP.keys())}"
            )
        engines.append(ENGINE_MAP[name])
    return engines


def main() -> None:
    args = arg_parser.parse_args()
    sizes: list[int] = sorted(args.size)
    operations: list[str] = args.operations
    engines = _resolve_engines(args.engines)

    engine_names = [e.name for e in engines]
    col_width = max(len(n) for n in engine_names + ["Engine"]) + 2

    # results[operation][engine_name] = [time_per_size...]
    results: dict[str, dict[str, list[float]]] = {
        op: {e.name: [] for e in engines} for op in operations
    }

    log_lines: list[str] = []

    for size in sizes:
        print(f"--- Benchmarking with {size} objects ---")
        humans = generate_humans(size)

        # Setup data for each engine (not timed)
        engine_data: dict[str, object] = {}
        for engine in engines:
            engine_data[engine.name] = engine.setup(humans)

        for op_name in operations:
            header = f"  [{op_name}]"
            print(header)
            log_lines.append(f"\n# size={size} operation={op_name}")
            log_lines.append(f"{'Engine':<{col_width}} Time [s]")

            for engine in engines:
                data = engine_data[engine.name]
                op_fn = getattr(engine, op_name)
                time_s = run_benchmark(op_fn, data)
                results[op_name][engine.name].append(time_s)

                line = f"    {engine.name:<{col_width}} {time_s:.6f}s"
                print(line)
                log_lines.append(f"{engine.name:<{col_width}} {time_s:.6f}")

    # Print summary
    if vars(args)["print"]:
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        for op_name in operations:
            print(f"\n--- {op_name} ---")
            header = f"{'Engine':<{col_width}}" + "".join(f"{s:>12}" for s in sizes)
            print(header)
            print("-" * len(header))
            for engine in engines:
                row = f"{engine.name:<{col_width}}" + "".join(
                    f"{t:>12.6f}" for t in results[op_name][engine.name]
                )
                print(row)

    if args.log is not None:
        with open(args.log, "w", encoding="utf-8") as f:
            f.write("\n".join(log_lines))
        print(f"\nLog saved to: {args.log}")

    if args.show or (args.img is not None):
        fig = plot_results(sizes, results, tested_version())
        if args.img is not None:
            fig.savefig(args.img, bbox_inches="tight", pad_inches=0.2, dpi=120)
            print(f"Chart saved to: {args.img}")
        if args.show:
            plt.show()


if __name__ == "__main__":
    main()
