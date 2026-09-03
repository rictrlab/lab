import torch

def solve(x: torch.Tensor, weight: torch.Tensor, bias: torch.Tensor) -> torch.Tensor:
    """Linear transformation.

    Args:
        x: Input tensor of shape (..., in_features)
        weight: Weight tensor of shape (out_features, in_features)
        bias: Bias tensor of shape (out_features,)

    Returns:
        Output tensor of shape (..., out_features)
    """
    pass
