import torch

def solve(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Batched matrix multiplication.

    Args:
        a: Tensor of shape (B, N, M)
        b: Tensor of shape (B, M, P)

    Returns:
        Tensor of shape (B, N, P) resulting from batched matmul.
    """
    pass
