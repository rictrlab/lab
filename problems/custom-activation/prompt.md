***Implement the Swish activation function, also known as SiLU (Sigmoid Linear Unit): It is applied element-wise.***

```python
>>> import torch
>>> x = torch.tensor([0., 1., -1.])
>>> solve(x)
tensor([ 0.0000,  0.7311, -0.2689])
>>> # 0 * sigmoid(0) = 0 * 0.5 = 0
>>> # 1 * sigmoid(1) ≈ 0.7311
>>> # -1 * sigmoid(-1) ≈ -0.2689
>>> solve(torch.tensor([2.]))
tensor([1.7616])
```

## Note
- Simplest: `return x * torch.sigmoid(x)`
- Equivalent to `torch.nn.functional.silu(x)`.

## Constraints
- Use `torch.sigmoid` (or manual `1/(1+exp(-x))`).
- Must preserve shape, dtype, and support autograd (output should be differentiable).
