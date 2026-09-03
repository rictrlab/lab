import torch

def solve(x: torch.Tensor, mask: torch.Tensor, value: float) -> torch.Tensor:
    return x.masked_fill(mask, value)
