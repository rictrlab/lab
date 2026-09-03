***Given two 1-D vectors `a` of shape `(N,)` and `b` of shape `(M,)`, compute their outer product as a matrix of shape `(N, M)` where `out[i, j] = a[i] * b[j]`.***

```python
>>> import torch
>>> a = torch.tensor([1., 2., 3.])
>>> b = torch.tensor([4., 5.])
>>> solve(a, b)
tensor([[ 4.,  5.],
        [ 8., 10.],
        [12., 15.]])
>>> a = torch.tensor([1, 2])
>>> b = torch.tensor([3, 4, 5])
>>> solve(a, b)
tensor([[ 3,  4,  5],
        [ 6,  8, 10]])
```

## Note
- Use `torch.outer(a, b)` or `torch.einsum('i,j->ij', a, b)` or `a[:, None] * b[None, :]`.

## Constraints
- Vectors are 1-D, lengths >=1.
- Accept both floating and integer dtypes.
