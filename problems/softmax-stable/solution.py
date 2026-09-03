import torch

def solve(x: torch.Tensor) -> torch.Tensor:
    x_max = x.max(dim=-1, keepdim=True).values
    e_x = torch.exp(x - x_max)
    return e_x / e_x.sum(dim=-1, keepdim=True)
