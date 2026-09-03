import torch

def solve(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Compute outer product of two vectors.

    Args:
        a: Tensor of shape (N,)
        b: Tensor of shape (M,)

    Returns:
        Tensor of shape (N, M) where out[i,j] = a[i]*b[j].
    """
    pass
