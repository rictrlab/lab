import torch

def solve(x: torch.Tensor) -> torch.Tensor:
    return x / x.norm(dim=1, keepdim=True)
