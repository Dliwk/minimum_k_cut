import json
import os
import random
import shutil
import time
from dataclasses import dataclass
import subprocess
from pathlib import Path
from pprint import pprint
import networkx as nx

APPROXIMATE_EXECUTABLE = 'cmake-build-release/approximate_algorithm'
NAIVE_EXECUTABLE = 'cmake-build-release/naive_algorithm'
GREEDY_EXECUTABLE = 'cmake-build-release/greedy_algorithm'

TESTS_DIR = Path(__file__).resolve().parent / 'test-groups'
REPORTS_DIR = Path(__file__).resolve().parent.parent / 'reports'

random.seed(20250514)


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


def generate_powerlaw_cluster_graph(k: int, n: int, p: float, max_weight: int) -> Test:
    m = n - 2
    graph = nx.powerlaw_cluster_graph(n, m, p)
    edges = [(i, j, random.randint(1, max_weight)) for (i, j) in graph.edges]
    return Test(n, m, k, edges)


def run_test_on(test: str, executable: str) -> RunResult:
    start_time = time.time()
    result = subprocess.run([executable], input=test.encode(), check=True, capture_output=True)
    run_time = time.time() - start_time
    return RunResult(output=int(result.stdout), time=run_time)


def run_and_compare_algorithms(test: str, first: str, second: str) -> Comparison:
    first_result = run_test_on(test, first)
    second_result = run_test_on(test, second)

    ratio = first_result.output / second_result.output if second_result.output != 0 else -1
    return Comparison(ratio, ratio, 1)


def read_test_group(name: str) -> list[str]:
    tests = []
    for test in (TESTS_DIR / name).iterdir():
        with open(test) as test_file:
            tests.append(test_file.read())
    return tests


def run_test_group(name: str, first: str, second: str) -> Comparison:
    tests = read_test_group(name)
    return merge_comparisons(*[run_and_compare_algorithms(test, first, second) for test in tests])


def run_benchmark_on_group(name: str) -> Benchmark:
    tests = read_test_group(name)
    return collect_benchmark(*[run_test_on(test, APPROXIMATE_EXECUTABLE) for test in tests])


def write_test_group(name: str, tests: list[Test]) -> None:
    group_dir = TESTS_DIR / name
    shutil.rmtree(group_dir, ignore_errors=True)
    group_dir.mkdir(exist_ok=True, parents=True)
    for i, test in enumerate(tests):
        with open(group_dir / f'{str(i)}.txt', 'w') as file:
            file.write(str(test))

def test_erdos_renyi_small(label: str, p: float, tests_count: int, subject: str, correct: str = NAIVE_EXECUTABLE):
    ratios_avg = []
    ratios_max = []
    for k in range(2, 12):
        ratios_avg.append([])
        ratios_max.append([])
        for n in range(k, 12):
            current_ratios = []
            for _ in range(tests_count):
                test = str(generate_random_graph(k, n, p, 1000))
                result_subject = run_test_on(test, subject)
                result_correct = run_test_on(test, correct)
                current_ratios.append(
                    result_subject.output / result_correct.output if result_correct.output != 0 else 1)
            ratios_avg[-1].append(sum(current_ratios) / len(current_ratios))
            ratios_max[-1].append(max(current_ratios))
    with open(REPORTS_DIR / f'erdos_renyi_small_{label}.json', 'w') as f:
        f.write(json.dumps({'max': ratios_max, 'avg': ratios_avg}))


def test_erdos_renyi_big(label: str, p: float, tests_count: int, subject: str, correct: str = NAIVE_EXECUTABLE):
    ratios_avg = []
    ratios_max = []
    for k in range(3, 13):
        ratios_avg.append([])
        ratios_max.append([])
        for n in range(50, 400, 50):
            current_ratios = []
            for _ in range(tests_count):
                test = str(generate_random_graph(k, n, p, 1000))
                result_subject = run_test_on(test, subject)
                result_correct = run_test_on(test, correct)
                current_ratios.append(
                    result_subject.output / result_correct.output if result_correct.output != 0 else 1)
            ratios_avg[-1].append(sum(current_ratios) / len(current_ratios))
            ratios_max[-1].append(max(current_ratios))
    with open(REPORTS_DIR / f'erdos_renyi_big_{label}.json', 'w') as f:
        f.write(json.dumps({'max': ratios_max, 'avg': ratios_avg}))


def run_group_and_print_results(group_name: str, first: str = APPROXIMATE_EXECUTABLE, second: str = NAIVE_EXECUTABLE):
    print(f'=== Running test group {group_name} ===')
    pprint(run_test_group(group_name, first, second))
    print()


def run_benchmark_and_print_results(group_name: str):
    print(f'=== Running benchmark on group {group_name} ===')
    pprint(run_benchmark_on_group(group_name))
    print()


if __name__ == '__main__':
    test_erdos_renyi_small('0.2-500', 0.2, 200, APPROXIMATE_EXECUTABLE)
    test_erdos_renyi_small('0.5-500', 0.5, 200, APPROXIMATE_EXECUTABLE)
    test_erdos_renyi_small('0.9-500', 0.9, 200, APPROXIMATE_EXECUTABLE)

    test_erdos_renyi_big('0.2', 0.2, 5, GREEDY_EXECUTABLE, APPROXIMATE_EXECUTABLE)
    test_erdos_renyi_big('0.5', 0.5, 5, GREEDY_EXECUTABLE, APPROXIMATE_EXECUTABLE)
    test_erdos_renyi_big('0.9', 0.9, 5, GREEDY_EXECUTABLE, APPROXIMATE_EXECUTABLE)
