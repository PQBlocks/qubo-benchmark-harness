from pqblocks_qubo_bench.tts_engine import calculate_tts

runs = [(0.012, True), (0.015, False), (0.011, True), (0.014, True)]
tts = calculate_tts(runs, 0.99)
print(f'Calculated TTS (99% target): {tts:.4f}s')
