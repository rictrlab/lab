***Implement a **single Adam optimization step** (as in Kingma & Ba, 2014).***

Given current parameter `param`, gradient `grad`, first moment `m`, second moment `v`, timestep `t`, and hyperparameters:

Return the updated `(param_new, m_new, v_new)`.

This is the exact update performed by `torch.optim.Adam` for a single step (without weight decay, amsgrad, or maximize).

```python
>>> import torch
>>> param = torch.tensor([1., 2.])
>>> grad = torch.tensor([0.1, 0.2])
>>> m = torch.zeros(2)
>>> v = torch.zeros(2)
>>> t = 1
>>> param_new, m_new, v_new = solve(param, grad, m, v, t)
>>> # m_new = 0.9*0 + 0.1*grad = [0.01, 0.02]
>>> # v_new = 0.999*0 + 0.001*grad^2 = [0.00001, 0.00004]
>>> # m_hat = m_new / (1-0.9^1) = [0.1, 0.2]
>>> # v_hat = v_new / (1-0.999^1) = [0.01, 0.04]
>>> # param_new = param - 0.001 * m_hat/(sqrt(v_hat)+1e-8)
```

```python
>>> param = torch.tensor([0.])
>>> grad = torch.tensor([1.])
>>> m = torch.zeros(1)
>>> v = torch.zeros(1)
>>> solve(param, grad, m, v, 1, lr=0.001)[0]
tensor([-0.0010])
```

## Note
- Use `torch.sqrt(v_hat)` or `v_hat.sqrt()`.
- Bias correction uses `1 - beta**t`; `**` works with floats.
- Return as tuple `(param_new, m_new, v_new)`.

## Constraints
- Preserve shape and dtype (compute in same dtype as param).
- `t` is `int` >=1.
- Do not mutate inputs in-place; return new tensors.
