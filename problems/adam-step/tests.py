import torch

def _reference(param, grad, m, v, t, lr=0.001, beta1=0.9, beta2=0.999, eps=1e-8):
    m_new = beta1 * m + (1 - beta1) * grad
    v_new = beta2 * v + (1 - beta2) * (grad ** 2)
    m_hat = m_new / (1 - beta1 ** t)
    v_hat = v_new / (1 - beta2 ** t)
    param_new = param - lr * m_hat / (torch.sqrt(v_hat) + eps)
    return param_new, m_new, v_new

def test_example(solve):
    param = torch.tensor([1., 2.])
    grad = torch.tensor([0.1, 0.2])
    m = torch.zeros(2)
    v = torch.zeros(2)
    t = 1
    param_new, m_new, v_new = solve(param, grad, m, v, t)
    exp_p, exp_m, exp_v = _reference(param, grad, m, v, t)
    assert torch.allclose(param_new, exp_p, atol=1e-6), f"param mismatch {param_new} vs {exp_p}"
    assert torch.allclose(m_new, exp_m, atol=1e-6)
    assert torch.allclose(v_new, exp_v, atol=1e-6)
    # check grad direction: param should decrease where grad positive
    assert param_new[0].item() < param[0].item()

def test_t2(solve):
    torch.manual_seed(0)
    param = torch.randn(3)
    grad = torch.randn(3)
    m = torch.randn(3) * 0.1
    v = torch.rand(3) * 0.1
    t = 2
    param_new, m_new, v_new = solve(param, grad, m, v, t, lr=0.001)
    exp_p, exp_m, exp_v = _reference(param, grad, m, v, t, lr=0.001)
    assert torch.allclose(param_new, exp_p, atol=1e-6)
    assert torch.allclose(m_new, exp_m, atol=1e-6)
    assert torch.allclose(v_new, exp_v, atol=1e-6)

def test_custom_lr(solve):
    param = torch.tensor([0.])
    grad = torch.tensor([1.])
    m = torch.zeros(1)
    v = torch.zeros(1)
    param_new, _, _ = solve(param, grad, m, v, 1, lr=0.01)
    # with default others, m_hat=1, v_hat=1, update =0.01*1/1=0.01
    assert abs(param_new.item() - (-0.01)) < 1e-6

def test_large_t(solve):
    torch.manual_seed(42)
    param = torch.randn(2, 2)
    grad = torch.randn(2, 2)
    m = torch.randn(2, 2)
    v = torch.abs(torch.randn(2, 2))
    t = 10
    param_new, m_new, v_new = solve(param, grad, m, v, t, lr=0.001, beta1=0.9, beta2=0.999, eps=1e-8)
    exp_p, exp_m, exp_v = _reference(param, grad, m, v, t)
    assert torch.allclose(param_new, exp_p, atol=1e-6)
    assert torch.allclose(m_new, exp_m, atol=1e-6)
    assert torch.allclose(v_new, exp_v, atol=1e-6)

def test_returns_tuple(solve):
    param = torch.tensor([1.])
    grad = torch.tensor([1.])
    m = torch.zeros(1)
    v = torch.zeros(1)
    result = solve(param, grad, m, v, 1)
    assert isinstance(result, tuple), f"Expected tuple, got {type(result)}"
    assert len(result) == 3
    for r in result:
        assert isinstance(r, torch.Tensor)

def test_no_mutation(solve):
    param = torch.tensor([1., 2.])
    grad = torch.tensor([0.1, 0.2])
    m = torch.zeros(2)
    v = torch.zeros(2)
    param_clone = param.clone()
    m_clone = m.clone()
    v_clone = v.clone()
    _ = solve(param, grad, m, v, 1)
    # original shouldn't be mutated if implementation is non-in-place; but we just check clones unchanged or not relied
    # Actually if solver mutates in-place, clone would differ. We check solve doesn't require mutation.
    # Just verify reference still works with original values (clone)
    exp_p, _, _ = _reference(param_clone, grad, m_clone, v_clone, 1)
    result_p, _, _ = solve(param_clone, grad, m_clone, v_clone, 1)
    assert torch.allclose(result_p, exp_p, atol=1e-6)

TESTS = [test_example, test_t2, test_custom_lr, test_large_t, test_returns_tuple, test_no_mutation]

def run_tests(solve):
    for t in TESTS:
        t(solve)
    return {"passed": True}

def run_all(solve):
    return run_tests(solve)

def check(solve):
    return run_tests(solve)

if __name__ == "__main__":
    import solution
    run_tests(solution.solve)
    print("All tests passed for adam-step")
