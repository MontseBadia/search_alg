## Decisions, Week 3

Why the setup is the way it is, and what got rejected. The settings themselves are in precommit.md.

### Tasks

- 30 of the 233 ARC-AGI-2 training tasks that aren't in ARC-AGI-1, seed 0.
  evaluation/ stays unseen for Solver v1 in Week 5. The 767 old ones are public since 2019, likely memorised.
  Checked by content, not just id: 766 of the old ones only have their pairs reordered, and none of the 233 shares a single pair with ARC-AGI-1.
- Rejected: 30 from evaluation/, even set aside from the Week 5 score. Solving them by hand teaches me the evaluation distribution, which then leaks into the DSL design.
- Pilot: 3 other tasks from the 203 left, never scored. The fallback excludes them: the same seed on the same pool would draw the pilot tasks first.

### Model

- Qwen3.8-27B, 4-bit MLX, local on the M4 Pro (24 GB), served by mlx_vlm.server.
  Frontier models are near the ceiling: Opus 5.5 93.3% on ARC-AGI-2 eval (arcprize.org, Sep 2026), too few failures to build a taxonomy from. Open weights also return the full thinking text, closed models only a summary. Free, fixed weights.
- Rejected:
  - DeepSeek-R1-0528-Qwen3-8B: runs, but likely ~0, too weak to say anything about abstraction
  - Dots3-Note: 280B, needs 8x H100
  - Claude Code headless: an agent with tools, could read the task JSON (test outputs included)
  - rented GPU + vLLM: hours instead of days, ~20-60 Eur, but thinking budget support unclear and different weights than the pilot
- Caveat for the write-up: results are about a strong open 27B model, not "frontier models".

### Thinking and tokens

- medium effort, thinking_budget 16000, max_tokens 22000.
  Without a budget the model thinks past 30000 tokens and never answers (f3e14006: 40 min, no answer). The budget forces </think> and then an answer. Works like a time limit: almost always a scoreable answer.
- medium = no instruction in the chat template (xhigh adds a "think carefully" sentence). On its own it didn't shorten the thinking.
- Answers after a forced stop are scored like any other, flagged maybe_forced.
- Rejected: thinking off (the reasoning just moves into the visible answer, still cut at 8000, no grid); a bigger budget (~40 min per call, days more).

### Samples

- Planned 3 per task, cut to 1. No seed in the request, mlx-vlm uses seed 0: calls run alone repeated sample 1 exactly (10 of 60), paired ones only drifted through batching float noise. Sample 2 isn't an independent sample, kept on record, never scored.
- Rejected: rerun samples 2 and 3 alone with a seed per call (~2 days, no time); pair solo calls with a dummy call to break the repeat (hacky, back at the memory limit).
- Any later run sends a seed per call from (task, variant, sample).
- Image variant dropped, for time. Text vs rule-first is the only comparison. Lost: the perception question (same model reading a picture vs digits), perception failures only judged from text transcripts.

### Prompt

- Digits separated by spaces: without them the tokenizer can merge "005" into one token.
- Not changed after the pilot failures (two answers exactly one row short). The failures are data, and tuning the prompt on 3 pilot tasks would be fitting the test. "Check against the actual grids" stays as an idea for a later variant or mechanism, not a patch.

### Memory and speed

- --kv-bits 8: cache 16 -> 8 bit, needed to fit, small quality risk. Peak 17.75-18.35 GB of the 19.07 GB the GPU can use.
- --prefill-step-size 512: prompt read in chunks. Same result (causal attention: each token only looks back, the cache carries the earlier chunks), less peak memory. A 7000-token prompt crashed without it.
- 2 calls at once (--max-num-seqs 2): ~1.6x throughput, the weights are read once per step for both. Only if the combined context stays under ~45000 tokens, the largest tasks run alone.
- The ~45000 limit is needed, not enough: 963c33f8 crashed paired at 39940, 985ae207 alone right after software update. Likely memory taken outside the server.
- Rejected: --kv-bits 4 (more risk on exact cell recall); raising the GPU memory limit.

### Run

Sample 1, from attempts.jsonl:
- Calls running 15.4 h (estimate was ~14 h)
- 60 calls with a response, 22.7 h model time (pairs overlap)
- Median 25.2 min, 3.6-29.6 min, none over 30
- 5 crashes (320afe60 x3, 963c33f8 x2), 1.8 h lost, all out of memory, all rerun

### Scoring

- Exact match on every test output. Main number: per-sample accuracy on sample 1 (= pass@1), against my 29/30.
- Secondary measures (rule components, outcome counts, shape correct) added before any scored run, because the pilot was 0/3: at zero accuracy the variants couldn't be compared otherwise.
- Rule outcome judged blind, before seeing any per-task score. Transcripts were read with answer grid hidden, no test outputs. Conventions in rule_components.md.

### Judging

- view.py hides the answer grids: I hand-solved the tasks, seeing the grid gives the score away. Draft grids inside the thinking stay visible, hiding them would also hide what perception judgments need.
- Only the final stated rule counts, earlier thinking doesn't, even if never taken back. Otherwise any component can be found somewhere in 900 lines of hypothesis testing.
- Strict wording replaced by "entailed counts": strict penalized rule-first, which the prompt caps at one or two sentences.
- Outcome order kept literal: any component -> not "wrong". Other rules that fit all train pairs go in the note, not under "underdetermined". Rejected: checking every partial row against the train pairs.
- judgments.csv in run order, not shuffled: both variants of a task read back to back, some drift between them accepted.

### Harness

- Kept:
  - atomic save: temp file + fsync + os.link. Never overwrites, never discards
  - crash records beside the result path, so the call gets rerun
  - attempt log: start/end per call, the proof that every scored result is a first completed attempt
  - failure classified by stage: refused = never started; failed while sending or no complete reply = crash
  - server check before every scored call: a manual restart after a crash, with a slightly different command, is the realistic mistake
  - runner (run_sample): fresh server per task. After an out-of-memory crash the old server failed the next call too 
  - run from Terminal.app
- Removed on purpose after review, simpler is enough for one person on one machine:
  - per-call locks: duplicates only come from my mistake, _dup + "first attempt counts" makes them harmless
  - F_FULLFSYNC + folder fsync: only matter for a power cut, the laptop has a battery
  - read-only SETTINGS: every result records its request, checkable in the report
  - proxy-ignoring opener: no proxy configured, and preflight would fail first
- Tests in arc/tests (unittest), never touch the real server or runs/main.

### Accepted limitations

- maybe_forced is a heuristic: the server only gives total tokens (thinking + answer), so a call is flagged when the total reaches 16000 even if thinking stopped on its own before the budget. Checked on s1 by counting the tokens of reasoning_content with the tokenizer: exact, all 45 flagged were forced
- the server's peak_memory is the highest since it started, not per call (two calls share one server)
- SETTINGS can be changed in a terminal: detectable from the results, not prevented
- the 233 are public since March 2025, the model may have seen them
- task difficulty isn't calibrated, only evaluation/ has the 66% human score
- forced stops: 45 of 60 sample 1 calls forced, thinking tokens counted (text 23/30, rule-first 22/30). Results are about the model with that budget, some wrong rules may just be where the thinking got cut
- one sample: no pass@2, no per-task check of systematic vs noisy failures
- judging conventions (stated rule only, entailed counts, partial before wrong, extras -> got rule) set after the first transcripts were judged
- outcome order: "wrong" only means no component at all, so partial mixes near misses with rules that fail their own train pairs
