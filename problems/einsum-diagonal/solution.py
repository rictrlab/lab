import torch

def solve(x: torch.Tensor) -> torch.Tensor:
    return torch.einsum('ii->i', x)
