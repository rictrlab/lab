import torch

def solve(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    return torch.outer(a, b)
