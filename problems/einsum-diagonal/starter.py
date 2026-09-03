import torch

def solve(x: torch.Tensor) -> torch.Tensor:
    """Extract diagonal using einsum.

    Args:
        x: Square tensor of shape (N, N)

    Returns:
        Tensor of shape (N,) containing diagonal elements.
    """
    pass
