***Given a tensor `x`, a boolean mask `mask` of the same shape, and a scalar `value`, return a new tensor where elements with `mask == True` are replaced by `value`, and others remain unchanged.***

This is the behavior of `torch.Tensor.masked_fill`.

```python
>>> import torch
>>> x = torch.tensor([[1., 2., 3.], [4., 5., 6.]])
>>> mask = torch.tensor([[True, False, True], [False, True, False]])
>>> solve(x, mask, -1)
tensor([[-1.,  2., -1.],
        [ 4., -1.,  6.]])
>>> x2 = torch.tensor([1, 2, 3, 4])
>>> mask2 = x2 > 2
>>> solve(x2, mask2, 0)
tensor([1, 2, 0, 0])
```

## Note
- `x.masked_fill(mask, value)` does exactly this.
- Note that `masked_fill` expects bool mask; if needed, ensure `mask` is bool.

## Constraints
- Must not mutate the input `x` in-place in a way that affects caller (return new tensor or correctly handle in-place but tests check functional behavior).
- Use `x.masked_fill(mask, value)`.
- Support any shape and dtype.
