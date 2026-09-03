***Given a 2-D tensor `x` of shape `(M, N)`, L2-normalize each row so that each row has Euclidean norm 1.***

Formally, for each row $i$:

$$
\hat{x}_i = \frac{x_i}{\|x_i\|_2}, \quad \|x_i\|_2 = \sqrt{\sum_j x_{i,j}^2}
$$

```python
>>> import torch
>>> x = torch.tensor([[3., 4.], [1., 2.]])
>>> solve(x)
tensor([[0.6000, 0.8000],
        [0.4472, 0.8944]])
>>> # Verify: norm of each row is 1
>>> solve(x).norm(dim=1)
tensor([1., 1.])
```

```python
>>> x = torch.tensor([[1., 1., 1.]])
>>> solve(x)
tensor([[0.5774, 0.5774, 0.5774]])
```

## Note
- Compute norm with `x.norm(dim=1, keepdim=True)` or `torch.norm(x, p=2, dim=1, keepdim=True)` or `torch.linalg.norm`.
- Broadcast division: `x / norm`.

## Constraints
- Rows are guaranteed non-zero (to avoid division by zero).
- Must preserve dtype and shape.
