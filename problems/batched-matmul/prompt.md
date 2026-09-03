***Given two batched matrices `a` of shape `(B, N, M)` and `b` of shape `(B, M, P)`, compute the batched matrix multiplication. Each batch element is an `N×M` matrix multiplied by an `M×P` matrix, yielding `B` results of shape `N×P`.***

Use `torch.bmm` or `torch.matmul` (which supports batching).

```python
>>> import torch
>>> a = torch.randn(2, 3, 4)
>>> b = torch.randn(2, 4, 5)
>>> solve(a, b).shape
torch.Size([2, 3, 5])
>>> # For B=2, each batch: (3x4) @ (4x5) -> (3x5)
```

```python
>>> a = torch.tensor([[[1., 2.], [3., 4.]]])  # shape (1,2,2)
>>> b = torch.tensor([[[5., 6.], [7., 8.]]])  # shape (1,2,2)
>>> solve(a, b)
tensor([[[19., 22.],
         [43., 50.]]])
```

## Note
- `torch.bmm(a, b)` does exactly this for 3D tensors.
- `torch.matmul(a, b)` also works and is more general.

## Constraints
- `B, N, M, P` are positive integers.
- Do not loop in Python over batch dimension; use vectorized op.
