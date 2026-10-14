# Local AI Lab — Model Benchmark Baseline

## 1. Purpose

This document records preliminary measurements from running local AI models through Ollama on the Local AI Lab development machine.

These results establish an initial baseline for future experiments. They are **not a controlled comparison or a definitive ranking** of model quality or performance.

## 2. Test environment

| Component | Configuration |
|---|---|
| Operating system | Ubuntu 26.04.1 LTS |
| Laptop | Lenovo LOQ 15IRX9 |
| GPU | NVIDIA GeForce RTX 3050 Laptop GPU |
| VRAM | 6 GB (6,144 MiB reported) |
| NVIDIA driver | 595.99.02 |
| CUDA reported by `nvidia-smi` | 13.2 |
| Inference runtime | Ollama 0.40.3 |
| Inference endpoint | `http://127.0.0.1:11434` |
| Execution type | Local inference; no cloud inference |

## 3. Installed models

| Model | Approximate size | Intended use |
|---|---:|---|
| `qwen2.5-coder:7b` | 4.7 GB | Code generation and programming assistance |
| `llama3.1:8b` | 4.9 GB | General-purpose chat |
| `deepseek-r1:1.5b` | 1.1 GB | Reasoning and lightweight tasks |
| `nomic-embed-text:latest` | 274 MB | Text embeddings |
| `llava:7b` | 4.7 GB | Image understanding and visual question answering |

Model sizes are approximate local storage figures, not peak memory requirements.

## 4. Preliminary results

### Text generation and reasoning

| Model | Test task | Total time | Generation speed | Observed VRAM | GPU allocation |
|---|---|---:|---:|---:|---|
| Qwen 2.5 Coder 7B | Python two-sum function and complexity explanation | 12.24 s | 35.1 tokens/s | 4,651 MiB | 100% GPU |
| DeepSeek R1 1.5B | Travel-time word problem | 4.40 s | 125.40 tokens/s | 1,233 MiB | 100% GPU |
| Llama 3.1 8B | Explain Python lists and dictionaries | 12.47 s | 27.26 tokens/s | 4,721 MiB | 86% GPU / 14% CPU |

The GPU allocation values are from `ollama ps`. VRAM figures are peak values observed during sampling and should be treated as approximate.

### Image understanding

| Model | Test input | Total time | Generation speed | Observed VRAM | GPU allocation |
|---|---|---:|---:|---:|---|
| LLaVA 7B | Screenshot of an electronic circuit diagram | 22.61 s | 28.39 tokens/s | Approximately 4,727 MB reported | 86% GPU / 14% CPU |

The prompt asked the model to describe the image, identify its main elements, explain visible text or diagrams, and acknowledge uncertainty.

The response identified a biased positive clipper circuit but appeared to infer some details that were not clearly established by the image. This is a qualitative observation, not a formal accuracy score.

### Text embeddings

| Model | Input type | Request time | Output dimensions | Observed VRAM | GPU allocation |
|---|---|---:|---:|---:|---|
| Nomic Embed Text | One text input | 1.48 s | 768 | Approximately 441 MB reported | 100% GPU |

Embedding measurements use request latency and vector dimensions rather than text-generation tokens per second. A single request does not establish embedding throughput.

## 5. Detailed inference measurements

The following measurements were returned by the Ollama API. Durations are converted from nanoseconds to seconds.

| Model | Load duration | Prompt tokens | Prompt evaluation | Output tokens | Output evaluation |
|---|---:|---:|---:|---:|---:|
| Qwen 2.5 Coder 7B | 6.072 s | 53 | 0.113 s | 212 | 6.044 s |
| DeepSeek R1 1.5B | 1.828 s | 36 | 0.055 s | 315 | 2.512 s |
| Llama 3.1 8B | 0.002 s | 30 | 0.207 s | 334 | 12.254 s |
| LLaVA 7B | 5.572 s | 617 | 0.850 s | 459 | 16.167 s |

**Important:** Llama 3.1 8B reported an unusually short load duration, suggesting that the model was already loaded or cached. Its load time should not be compared with the other models as a cold-start measurement.

## 6. Method and limitations

- Models were tested locally through the Ollama API.
- Each generation model received a task appropriate to its intended use; prompts and output lengths therefore differ.
- Measurements reflect individual runs, not averages over repeated trials.
- Model load state was not consistent across all runs.
- VRAM values are sampled observations, not exact measurements of memory attributable solely to each model.
- GPU/CPU allocation reflects Ollama's reported model placement and does not measure overall inference quality.
- Response quality was assessed informally, without a standardized evaluation dataset.
- Results can change with model versions, quantization, context length, system load, runtime settings, drivers, and hardware.
- Embedding latency from one input is not a throughput benchmark.

For these reasons, generation speeds are useful as an initial reference, but the results should not be treated as an apples-to-apples ranking.

## 7. Future benchmark improvements

- [ ] Repeat each test several times and report median latency and tokens per second.
- [ ] Separate cold-start and warm-run measurements.
- [ ] Use consistent prompts and output-length limits where model capabilities permit.
- [ ] Record model tags, quantization details, and relevant runtime settings.
- [ ] Capture GPU memory before, during, and after inference using a consistent sampling method.
- [ ] Evaluate output quality against expected answers or a small repeatable test set.
- [ ] Measure embedding throughput across a batch of inputs.
- [ ] Add a reproducible benchmark script that saves raw API metrics and environment details.

---

*This baseline records observed results from the Local AI Lab development environment. Update it when tests are repeated under a more controlled procedure.*
