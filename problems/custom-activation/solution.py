import torch

def solve(x: torch.Tensor) -> torch.Tensor:
    return x * torch.sigmoid(x)
