***Create a 3×3 tensor containing the values 0 through 8 in row-major order.***

You must use PyTorch operations to construct the tensor. The output should be a `torch.Tensor` of shape `(3, 3)` with dtype `torch.int64` (default for `torch.arange`).

```python
>>> solve()
tensor([[0, 1, 2],
        [3, 4, 5],
        [6, 7, 8]])
>>> solve().shape
torch.Size([3, 3])
>>> solve().dtype
torch.int64
```

## Note
- `torch.arange` creates a 1-D range.
- `.reshape` or `.view` changes shape.

## Constraints
- The returned tensor must be exactly `torch.arange(9).reshape(3,3)` (or equivalent).
