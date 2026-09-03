***Given two tensors `a` of shape `(3, 1)` and `b` of shape `(1, 4)`, compute their sum using broadcasting. The result should have shape `(3, 4)`.***

Broadcasting should happen automatically via PyTorch's `+` operator.

```python
>>> import torch
>>> a = torch.tensor([[1.], [2.], [3.]])
>>> b = torch.tensor([[10., 20., 30., 40.]])
>>> solve(a, b)
tensor([[11., 21., 31., 41.],
        [12., 22., 32., 42.],
        [13., 23., 33., 43.]])
>>> solve(a, b).shape
torch.Size([3, 4])
```

## Note
- PyTorch broadcasting follows NumPy rules.
- Simply `return a + b` is sufficient.

## Constraints
- Do not manually expand or tile; rely on broadcasting (`a + b`).
- Input tensors will be floating point.
