***Implement a fully-connected **linear layer** (also called `nn.Linear`): Do not use `torch.nn.Linear` or `F.linear`; implement manually via matrix multiplication.***

```python
>>> import torch
>>> x = torch.tensor([[1., 2., 3.]])
>>> weight = torch.tensor([[1., 0., 0.],
...                        [0., 1., 0.]])
>>> bias = torch.tensor([10., 20.])
>>> solve(x, weight, bias)
tensor([[11., 22.]])
>>> # x @ weight.T = [[1,2]] ; + bias => [[11,22]]

>>> x2 = torch.randn(2, 4)
>>> w = torch.randn(5, 4)
>>> b = torch.randn(5)
>>> solve(x2, w, b).shape
torch.Size([2, 5])
```

## Note
- `x @ weight.T` works via broadcasting matmul, or use `torch.matmul`.
- Then add `bias` (broadcasts over leading dims).

## Constraints
- Support batched leading dimensions (any `...`).
- Preserve dtype.
