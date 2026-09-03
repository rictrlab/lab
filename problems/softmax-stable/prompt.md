***Implement a **numerically stable softmax** along the last dimension.***

Naive softmax $\text{softmax}(x)_i = \frac{e^{x_i}}{\sum_j e^{x_j}}$ can overflow for large values. The stable version subtracts the maximum:

$$
\text{softmax}(x)_i = \frac{e^{x_i - \max(x)}}{\sum_j e^{x_j - \max(x)}}
$$

```python
>>> import torch
>>> x = torch.tensor([1., 2., 3.])
>>> solve(x)
tensor([0.0900, 0.2447, 0.6652])
>>> solve(x).sum()
tensor(1.)
>>> # Large values still stable:
>>> solve(torch.tensor([1000., 1000., 1000.]))
tensor([0.3333, 0.3333, 0.3333])
>>> # 2D case
>>> x2 = torch.tensor([[1., 2., 3.], [1., 1., 1.]])
>>> solve(x2)
tensor([[0.0900, 0.2447, 0.6652],
        [0.3333, 0.3333, 0.3333]])
```

## Note
- `x_max = x.max(dim=-1, keepdim=True).values`
- `torch.exp(x - x_max) / torch.exp(x - x_max).sum(dim=-1, keepdim=True)`

## Constraints
- Must subtract max for stability.
- Apply along `dim=-1`.
- Must handle large inputs (e.g., 1e3) without overflow/nan.
