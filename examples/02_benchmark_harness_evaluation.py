"""Example 02: Loading benchmark problem instances and evaluating solver baselines."""

import dimod
from pqblocks_qubo_bench.gap import calculate_gap
from pqblocks_qubo_bench.loaders import load_instance
from pqblocks_qubo_bench.tts_engine import calculate_tts


def main():
    print("--- Benchmark Instance Loading ---")
    bqm, meta = load_instance("gset", "G1")
    print(f"Loaded instance: {meta['instance_id']} ({meta['suite_name']})")
    print(f"Variables: {len(bqm.variables)}, Linear biases: {len(bqm.linear)}, Quadratic: {len(bqm.quadratic)}")

    print("\n--- Evaluating Solution Quality and Reference Gap ---")
    reference_optimum = -6.0
    trial_energies = [-6.0, -5.5, -6.0, -4.8, -6.0]
    timing_runs = []

    for idx, e in enumerate(trial_energies):
        gap = calculate_gap(e, reference_optimum)
        hit_target = abs(gap) < 1e-4 if gap is not None else False
        runtime = 0.005 + (idx * 0.001)
        timing_runs.append((runtime, hit_target))
        print(f"Run {idx + 1}: energy={e:6.1f}, gap={gap:.4f}, success={hit_target}")

    tts_99 = calculate_tts(timing_runs, target_prob=0.99)
    print(f"\nTime-To-Solution (TTS @ 99% confidence): {tts_99:.6f}s")
    print("Benchmark evaluation completed successfully.")


if __name__ == "__main__":
    main()
