import torch

def solve(x: torch.Tensor, mask: torch.Tensor, value: float) -> torch.Tensor:
    """Masked fill operation.

    Args:
        x: Tensor of any shape
        mask: Boolean tensor of same shape as x
        value: Scalar value to fill where mask is True

    Returns:
        Tensor with masked values filled.
    """
    pass
