import torch

def solve(param: torch.Tensor, grad: torch.Tensor, m: torch.Tensor, v: torch.Tensor, t: int, lr: float = 0.001, beta1: float = 0.9, beta2: float = 0.999, eps: float = 1e-8):
    m_new = beta1 * m + (1 - beta1) * grad
    v_new = beta2 * v + (1 - beta2) * (grad ** 2)
    m_hat = m_new / (1 - beta1 ** t)
    v_hat = v_new / (1 - beta2 ** t)
    param_new = param - lr * m_hat / (torch.sqrt(v_hat) + eps)
    return param_new, m_new, v_new
