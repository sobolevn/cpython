"""Microbenchmarks for the stdlib ``re`` engine.

The suite covers several regex features over multiple input sizes and reports
matches/second.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import timeit


SIZES = {
    "tiny": 32,
    "small": 256,
    "medium": 4096,
    "large": 65536,
}

INNER_LOOPS = {
    "tiny": 800,
    "small": 400,
    "medium": 120,
    "large": 20,
}


def _literal_text(size: int) -> str:
    return ("x" * max(size - 6, 0)) + "needle"


def _charset_text(size: int) -> str:
    return ("Ab0_" * ((size + 3) // 4))[:size]


def _quantifier_text(size: int) -> str:
    unit = max(size // 3, 1)
    return ("a" * unit) + ("b" * unit) + ("c" * unit)


def _alternation_text(size: int) -> str:
    prefix = "xyz" * (size // 3)
    return prefix + "abcdefghijkl"


def _backref_text(size: int) -> str:
    token = ("abcd" * ((size + 3) // 4))[:max(size, 1)]
    return f"{token}-{token}-{token}"


def _lookaround_text(size: int) -> str:
    return "foobarbaz" * max(size // 9, 1)


CASES = (
    {
        "name": "literal-search",
        "pattern": r"needle",
        "builder": _literal_text,
        "runner": lambda pat, text: pat.search(text),
    },
    {
        "name": "charset-fullmatch",
        "pattern": r"[A-Za-z0-9_]+",
        "builder": _charset_text,
        "runner": lambda pat, text: pat.fullmatch(text),
    },
    {
        "name": "greedy-quantifier-fullmatch",
        "pattern": r"a+b+c+",
        "builder": _quantifier_text,
        "runner": lambda pat, text: pat.fullmatch(text),
    },
    {
        "name": "alternation-search",
        "pattern": r"(?:abc|def|ghi|jkl){4}",
        "builder": _alternation_text,
        "runner": lambda pat, text: pat.search(text),
    },
    {
        "name": "groupref-fullmatch",
        "pattern": r"([a-z]+)-\1-\1",
        "builder": _backref_text,
        "runner": lambda pat, text: pat.fullmatch(text),
    },
    {
        "name": "lookaround-findall",
        "pattern": r"(?<=foo)bar(?=baz)",
        "builder": _lookaround_text,
        "runner": lambda pat, text: pat.findall(text),
    },
)


def _measure(runner, *, seconds: float, repeat: int, scale: int) -> list[float]:
    timer = timeit.Timer(runner)
    values = []
    for _ in range(repeat):
        total_time = 0.0
        count = 0
        while total_time < seconds:
            total_time += timer.timeit(1)
            count += 1
        if total_time > seconds:
            count -= 1
        values.append((count * scale) / seconds)
    return values


def _format_speed(value: float) -> str:
    return f"{value:,.0f} matches/s"


def run_benchmarks(*, sizes: list[str], seconds: float, repeat: int, case_filter: str | None) -> dict[str, list[float]]:
    results: dict[str, list[float]] = {}
    selected = [c for c in CASES if case_filter is None or c["name"] == case_filter]
    if not selected:
        raise ValueError(f"unknown benchmark case: {case_filter!r}")

    for size_name in sizes:
        size = SIZES[size_name]
        inner_loops = INNER_LOOPS[size_name]
        for case in selected:
            key = f"{case['name']}[{size_name}]"
            compiled = re.compile(case["pattern"])
            text = case["builder"](size)

            probe = case["runner"](compiled, text)
            if probe is None:
                raise RuntimeError(f"{key} did not match probe input")

            def one_round() -> None:
                for _ in range(inner_loops):
                    case["runner"](compiled, text)

            speeds = _measure(one_round, seconds=seconds, repeat=repeat, scale=inner_loops)
            results[key] = speeds
            print(f"{key:36} best={_format_speed(max(speeds))} values={[int(v) for v in speeds]}")
            sys.stdout.flush()
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--size",
        choices=tuple(SIZES),
        action="append",
        dest="sizes",
        help="input size to run (repeatable). Defaults to all sizes.",
    )
    parser.add_argument(
        "--seconds",
        type=float,
        default=0.7,
        help="measurement window per repeat (default: 0.7s)",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=5,
        help="number of repeats per benchmark (default: 5)",
    )
    parser.add_argument(
        "--case",
        dest="case_filter",
        help="run only one case by name",
    )
    parser.add_argument(
        "--read",
        dest="read_file",
        help="read prior JSON results and compare",
    )
    parser.add_argument(
        "--write",
        dest="write_file",
        help="write JSON results",
    )
    args = parser.parse_args()

    sizes = args.sizes or list(SIZES)
    print(f"Running re benchmarks: sizes={sizes}, repeat={args.repeat}, seconds={args.seconds}")
    results = run_benchmarks(
        sizes=sizes,
        seconds=args.seconds,
        repeat=args.repeat,
        case_filter=args.case_filter,
    )

    if args.read_file:
        with open(args.read_file, encoding="utf-8") as f:
            prior = json.load(f)
        print("\nComparison against prior run:")
        for key in sorted(results):
            if key not in prior:
                continue
            current = max(results[key])
            previous = max(prior[key])
            if previous <= 0:
                continue
            ratio = current / previous
            print(f"{key:36} {_format_speed(current):>18} vs {_format_speed(previous):>18} ({ratio:6.2%})")

    if args.write_file:
        with open(args.write_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, sort_keys=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
