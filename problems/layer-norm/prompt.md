***Implement **Layer Normalization** without using `torch.nn.LayerNorm` or `torch.nn.functional.layer_norm`. You must compute it manually.***

Given input `x` of shape `(..., D)`, normalize over the last dimension:

$$
\hat{x} = \frac{x - \mu}{\sqrt{\sigma^2 + \epsilon}}, \quad y = \gamma \odot \hat{x} + \beta
$$

where $\mu = \frac{1}{D}\sum_{i=1}^{D} x_i$ and $\sigma^2 = \frac{1}{D}\sum_{i=1}^{D} (x_i - \mu)^2$.

```python
>>> import torch
>>> x = torch.tensor([[1., 2., 3.], [4., 5., 6.]])
>>> gamma = torch.ones(3)
>>> beta = torch.zeros(3)
>>> solve(x, gamma, beta)
tensor([[-1.2247,  0.0000,  1.2247],
        [-1.2247,  0.0000,  1.2247]])
>>> # With gamma=2, beta=1
>>> solve(x, torch.tensor([2., 2., 2.]), torch.tensor([1., 1., 1.]))
tensor([[-1.4494,  1.0000,  3.4494],
        [-1.4494,  1.0000,  3.4494]])
```

## Note
- `mean = x.mean(dim=-1, keepdim=True)`
- `var = x.var(dim=-1, keepdim=True, unbiased=False)` or `((x - mean)**2).mean(dim=-1, keepdim=True)`
- `x_hat = (x - mean) / torch.sqrt(var + eps)`

## Constraints
- Do **not** use `torch.nn.LayerNorm` or `F.layer_norm`; implement formula manually.
- Use `unbiased=False` for variance (population variance).
- Must handle any leading dimensions (normalize only last dim).
- Preserve dtype.
