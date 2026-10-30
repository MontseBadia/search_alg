# How to run

All commands from arc/. Activate the venv in every new terminal:
```
source .venv/bin/activate
```

## 1. Setup (once)

Install venv + mlx-vlm:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -U mlx-vlm
```

Check that MLX sees the GPU:
```
python -c "import mlx.core as mx; print(mx.default_device())"
```

Run smoke test, this also downloads the model (16 GB, takes a while):
```
mlx_vlm.generate --model mlx-community/Qwen3.8-27B-4bit --enable-thinking --max-tokens 500 --prompt "What is 17 + 25?"
```

## 2. Setup checks (history)

Try a tiny ARC-like transformation (`--verbose` for stats):
```
mlx_vlm.generate --model mlx-community/Qwen3.8-27B-4bit --enable-thinking --verbose --max-tokens 1500 \
  --prompt "A 3x3 grid has rows 1 2 3 / 4 5 6 / 7 8 9. Rotate it 90 degrees clockwise and then mirror it left to right. Give the final grid."
```

Use a longer prompt (it crashed):
```
mlx_vlm.generate --model mlx-community/Qwen3.8-27B-4bit --verbose --max-tokens 20 \
  --prompt "$(python3 -c "import random; print('\n'.join(' '.join(str(random.randint(0,9)) for _ in range(30)) for _ in range(120)))") Reply only OK."
```

Fixed by reading the prompt in chunks (see decisions.md):
```
mlx_vlm.generate --model mlx-community/Qwen3.8-27B-4bit --verbose --max-tokens 20 --prefill-step-size 512 \
  --prompt "$(python3 -c "import random; print('\n'.join(' '.join(str(random.randint(0,9)) for _ in range(30)) for _ in range(120)))") Reply only OK."
```

## 3. Pilot (not scored)

Server, frozen settings (prints the command to paste):
```
python3 -c "import harness as h; print(h.paste_command())"
```

As printed above, MLX_VLM_LOG_PROGRESS_INTERVAL=100 prints fewer server logs (a progress line every 100 tokens instead of 10):
```
MLX_VLM_LOG_PROGRESS_INTERVAL=100 caffeinate -i mlx_vlm.server --model mlx-community/Qwen3.8-27B-4bit --port 8080 --kv-bits 8 --prefill-step-size 512 --max-num-seqs 2
```

Then from a second terminal:
```
caffeinate -i python3 -c "import harness as h; print(h.pilot_call('f3e14006', 'text', 'medium30k'))"
```
pilot_call takes setting overrides, e.g. `max_tokens=500`. Results in runs/pilot/.

Via library instead, kept as record:
```
mkdir -p runs/pilot
mlx_vlm.generate --model mlx-community/Qwen3.8-27B-4bit --enable-thinking --verbose \
  --temperature 1.0 --top-p 0.95 --top-k 20 \
  --kv-bits 8 --prefill-step-size 512 --max-tokens 12000 \
  --prompt "$(python3 -c 'import harness as h; print(h.build_prompt(h.load_task("f3e14006"), "text"))')" \
  | tee runs/pilot/f3e14006_text_manual.txt
```

## 4. Run a sample

From new terminal:
```
python3 -c "import harness as h; h.run_sample(1)"
```
- fresh server per task, both variants at once, ALONE tasks one call at a time
- stops at the first call that isn't a clean response
- resume: same command, calls with a result file are skipped
- after a crash: an error lands on the result path, rename it to <name>_crash.json
  or the resume skips it. Log it under Changes in precommit
- server log: runs/main/server_s<k>.log

Manual fallback, one call at a time. It needs a server running.
```
caffeinate -i python3 -c "import harness as h; h.run_call('5623160b', 'text', 1)"
```

## 5. Tests

From the repo root:
```
python3 -m unittest discover arc/tests
```

## 6. Judge (blind)

Read one transcript to see reasoning, answer grids are hidden:
```
python3 view.py 7ec998c9 text 1 | less
python3 view.py 7ec998c9 rule_first 1 | less
```
Fill runs/main/judgments.csv. Conventions in notes/rule_components.md.

## 7. Score

Analysis script.
