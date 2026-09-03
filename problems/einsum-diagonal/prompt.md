***Given a square matrix `x` of shape `(N, N)`, extract its diagonal as a 1-D tensor of shape `(N,)` using `torch.einsum`.***

Your solution must use `torch.einsum` with the equation `'ii->i'` (or equivalent). While `torch.diag` would also work, the purpose of this puzzle is to practice einsum notation.

```python
>>> import torch
>>> x = torch.tensor([[1, 2, 3],
...                   [4, 5, 6],
...                   [7, 8, 9]])
>>> solve(x)
tensor([1, 5, 9])
>>> y = torch.tensor([[10., 20.],
...                   [30., 40.]])
>>> solve(y)
tensor([10., 40.])
```

## Note
- `torch.einsum('ii->i', x)` extracts the diagonal by summing over the implicit? No, `'ii->i'` keeps elements where both indices are equal.
- Equivalent to `torch.diagonal(x)` but with einsum syntax.

## Constraints
- Input is always square (N >= 1).
- Use `torch.einsum` with `'ii->i'`.
- Must work for any dtype and device (CPU).
