import torch

def solve(param: torch.Tensor, grad: torch.Tensor, m: torch.Tensor, v: torch.Tensor, t: int, lr: float = 0.001, beta1: float = 0.9, beta2: float = 0.999, eps: float = 1e-8):
    """Single Adam step.

    Args:
        param: Current parameter tensor
        grad: Gradient tensor same shape as param
        m: First moment estimate
        v: Second moment estimate
        t: Timestep (1-indexed)
        lr: Learning rate
        beta1: Exponential decay for first moment
        beta2: Exponential decay for second moment
        eps: Small constant for numerical stability

    Returns:
        Tuple (param_new, m_new, v_new) updated tensors.
    """
    pass
