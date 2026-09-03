# RictrLab — PyTorch-Native Tensortonic

**CPU-only MVP** — Tensortonic-like platform where every problem is solved with `torch.*`, not NumPy.

* 12 PyTorch-native puzzles (Tensor Maniacs / Autograd / nn.Module)
* Monaco Editor + FastAPI Judge (torch CPU, 2 threads, deterministic, 5s timeout)
* Dark Tensortonic-inspired UI
* $0 infra: FastAPI + Next.js + SQLite + Docker-ready

## Running

```
./serve.sh
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# Docs:     http://localhost:8000/docs
# Health:   http://localhost:8000/api/health
```

Manual:
```bash
# Backend
cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
# Frontend
cd frontend && npm install && npm run build && npm run start
```

## API Examples

```bash
# Health
curl http://localhost:8000/api/health
# List problems
curl http://localhost:8000/api/problems
# Detail
curl http://localhost:8000/api/problems/tensor-creation
# Submit (correct)
curl -X POST http://localhost:8000/api/submit -H "Content-Type: application/json" \
  -d '{"slug":"tensor-creation","code":"import torch\ndef solve():\n    return torch.arange(9).reshape(3,3)"}'
# Submit (fail)
curl -X POST http://localhost:8000/api/submit -H "Content-Type: application/json" \
  -d '{"slug":"softmax-stable","code":"import torch\ndef solve(x):\n    return x"}'
```

## Problems

| ID | Slug | Category | Difficulty |
|----|------|----------|------------|
| 1 | tensor-creation | Tensor Maniacs | Easy |
| 2 | tensor-broadcast | Tensor Maniacs | Easy |
| 3 | batched-matmul | Tensor Maniacs | Easy |
| 4 | einsum-diagonal | Tensor Maniacs | Medium |
| 5 | normalized-rows | Tensor Maniacs | Medium |
| 6 | outer-product | Tensor Maniacs | Easy |
| 7 | masked-fill | Tensor Maniacs | Medium |
| 8 | custom-activation | Autograd | Medium |
| 9 | layer-norm | nn.Module | Hard |
| 10 | linear-layer | nn.Module | Medium |
| 11 | softmax-stable | Autograd | Medium |
| 12 | adam-step | Autograd | Hard |

All `solution.py` pass (4-6 hidden tests each, ~1s judge latency, CPU-only).

## CPU Execution

- `torch==2.5.1+cpu`, `OMP_NUM_THREADS=2`, `torch.set_num_threads(2)`, `torch.use_deterministic_algorithms(True)`
- Judge: writes `user_code.py` + `harness.py` to tmpdir, `subprocess.run` timeout 5s, `__import__` blocked via AST, `CUDA_VISIBLE_DEVICES=""`, no network, 512m limit (Docker-ready)
- Free tier: Oracle Free Ampere (4 OCPU 24GB) or Cloud Run + Vercel + Neon/Supabase

## Stack

Frontend: Next.js 14, TypeScript, Tailwind, @monaco-editor/react, react-markdown
Backend: FastAPI, SQLAlchemy (SQLite), Pydantic, uvicorn, torch CPU
