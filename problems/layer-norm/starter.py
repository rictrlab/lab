import torch

def solve(x: torch.Tensor, gamma: torch.Tensor, beta: torch.Tensor, eps: float = 1e-5) -> torch.Tensor:
    """Layer Normalization.

    Args:
        x: Input tensor of shape (..., D)
        gamma: Scale parameter of shape (D,)
        beta: Shift parameter of shape (D,)
        eps: Small constant for stability

    Returns:
        Layer-normalized tensor of same shape as x.
    """
    pass
