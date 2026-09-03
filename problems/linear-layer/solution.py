import torch

def solve(x: torch.Tensor, weight: torch.Tensor, bias: torch.Tensor) -> torch.Tensor:
    return x @ weight.T + bias
