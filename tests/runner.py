import os
import random
import shutil
import time
from dataclasses import dataclass
import subprocess
from pathlib import Path
from pprint import pprint

APPROXIMATE_EXECUTABLE = 'cmake-build-release/approximate_algorithm'
NAIVE_EXECUTABLE = 'cmake-build-release/naive_algorithm'

TESTS_DIR = Path(__file__).resolve().parent


@dataclass
class Test:
    n: int
    m: int
    k: int
    edges: list[tuple[int, int, int]]

    def __str__(self) -> str:
        return (f'{self.n} {self.m} {self.k}\n'
                + '\n'.join(f'{u + 1} {v + 1} {w + 1}' for (u, v, w) in self.edges))


@dataclass
class RunResult:
    output: int
    time: float


@dataclass
class Benchmark:
    worst_time: float
    average_time: float


@dataclass
class Comparison:
    worst_ratio: float
    average_ratio: float
    tests_count: int


def merge_comparisons(*results: Comparison) -> Comparison:
    tests_count = sum(result.tests_count for result in results)
    return Comparison(max(result.worst_ratio for result in results),
                      sum(result.average_ratio * result.tests_count for result in results) / tests_count,
                      tests_count)


def collect_benchmark(*results: RunResult) -> Benchmark:
    return Benchmark(max(result.time for result in results),
                     sum(result.time for result in results) / len(results))


def generate_random_graph(k: int, n: int, p: float, max_weight: int) -> Test:
    print(f'-- Generating graph ({k=}, {n=}, {p=}, {max_weight=})')
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < p:
                edges.append((i, j, random.randint(0, max_weight)))
    return Test(n, len(edges), k, edges)


def run_test_on(test: str, executable: str) -> RunResult:
    start_time = time.time()
    result = subprocess.run([executable], input=test.encode(), check=True, capture_output=True)
    run_time = time.time() - start_time
    return RunResult(output=int(result.stdout), time=run_time)


def run_and_compare_algorithms(test: str) -> Comparison:
    approximate_result = run_test_on(test, APPROXIMATE_EXECUTABLE)
    naive_result = run_test_on(test, NAIVE_EXECUTABLE)

    ratio = approximate_result.output / naive_result.output
    return Comparison(ratio, ratio, 1)


def read_test_group(name: str) -> list[str]:
    tests = []
    for test in (TESTS_DIR / name).iterdir():
        with open(test) as test_file:
            tests.append(test_file.read())
    return tests


def run_test_group(name: str) -> Comparison:
    tests = read_test_group(name)
    return merge_comparisons(*[run_and_compare_algorithms(test) for test in tests])


def run_benchmark_on_group(name: str) -> Benchmark:
    tests = read_test_group(name)
    return collect_benchmark(*[run_test_on(test, APPROXIMATE_EXECUTABLE) for test in tests])


def write_test_group(name: str, tests: list[Test]) -> None:
    group_dir = TESTS_DIR / name
    shutil.rmtree(group_dir, ignore_errors=True)
    group_dir.mkdir(exist_ok=True)
    for i, test in enumerate(tests):
        with open(group_dir / f'{str(i)}.txt', 'w') as file:
            file.write(str(test))


def write_test_groups():
    write_test_group('2-cut-small', [
        generate_random_graph(2, 2, 1.0, 10),
        generate_random_graph(2, 3, 1.0, 10),
        generate_random_graph(2, 5, 1.0, 100),
        generate_random_graph(2, 7, 1.0, 100),
        generate_random_graph(2, 8, 1.0, 1000),
        generate_random_graph(2, 10, 1.0, 1000),
        generate_random_graph(2, 12, 1.0, 1000),
    ])

    write_test_group('3-cut-small', [
        generate_random_graph(3, 3, 1.0, 1000),
        generate_random_graph(3, 12, 1.0, 1000),
        generate_random_graph(3, 12, 0.9, 1000),
        generate_random_graph(3, 12, 0.8, 1000),
        generate_random_graph(3, 12, 0.7, 1000),
        generate_random_graph(3, 12, 0.6, 1000),
        generate_random_graph(3, 12, 0.5, 1000),
    ])

    write_test_group('4-cut-small', [
        generate_random_graph(4, 4, 1.0, 1000),
        generate_random_graph(4, 12, 1.0, 1000),
        generate_random_graph(4, 12, 0.9, 1000),
        generate_random_graph(4, 12, 0.8, 1000),
        generate_random_graph(4, 12, 0.7, 1000),
        generate_random_graph(4, 12, 0.6, 1000),
        generate_random_graph(4, 12, 0.5, 1000),
    ])

    write_test_group('100-vertices', [
        generate_random_graph(random.randint(2, 90), 100, random.uniform(0.2, 0.8), 1000)
        for _ in range(20)
    ])

    write_test_group('200-vertices', [
        generate_random_graph(random.randint(2, 190), 200, random.uniform(0.2, 0.8), 1000)
        for _ in range(20)
    ])

    write_test_group('400-vertices', [
        generate_random_graph(random.randint(2, 390), 400, random.uniform(0.2, 0.8), 1000)
        for _ in range(20)
    ])

    write_test_group('800-vertices', [
        generate_random_graph(random.randint(2, 790), 800, random.uniform(0.2, 0.8), 1000)
        for _ in range(20)
    ])


def run_group_and_print_results(group_name: str):
    print(f'=== Running test group {group_name} ===')
    pprint(run_test_group(group_name))
    print()


def run_benchmark_and_print_results(group_name: str):
    print(f'=== Running benchmark on group {group_name} ===')
    pprint(run_benchmark_on_group(group_name))
    print()


if __name__ == '__main__':
    # write_test_groups()
    # print()

    run_group_and_print_results('2-cut-small')
    run_group_and_print_results('3-cut-small')
    run_group_and_print_results('4-cut-small')

    run_benchmark_and_print_results('100-vertices')
    run_benchmark_and_print_results('200-vertices')
    run_benchmark_and_print_results('400-vertices')
    run_benchmark_and_print_results('800-vertices')
