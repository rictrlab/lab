import torch
import torch.nn.functional as F

def test_example(solve):
    x = torch.tensor([[1., 2., 3.], [4., 5., 6.]])
    gamma = torch.ones(3)
    beta = torch.zeros(3)
    result = solve(x, gamma, beta)
    expected = F.layer_norm(x, (3,), weight=gamma, bias=beta, eps=1e-5)
    assert torch.allclose(result, expected, atol=1e-5), f"Expected {expected}, got {result}"

def test_gamma_beta(solve):
    x = torch.tensor([[1., 2., 3.], [4., 5., 6.]])
    gamma = torch.tensor([2., 2., 2.])
    beta = torch.tensor([1., 1., 1.])
    result = solve(x, gamma, beta, eps=1e-5)
    expected = F.layer_norm(x, (3,), weight=gamma, bias=beta, eps=1e-5)
    assert torch.allclose(result, expected, atol=1e-5)

def test_random_2d(solve):
    torch.manual_seed(0)
    x = torch.randn(4, 8)
    gamma = torch.randn(8)
    beta = torch.randn(8)
    result = solve(x, gamma, beta, eps=1e-5)
    expected = F.layer_norm(x, (8,), weight=gamma, bias=beta, eps=1e-5)
    assert torch.allclose(result, expected, atol=1e-5)

def test_3d(solve):
    torch.manual_seed(1)
    x = torch.randn(2, 3, 4)
    gamma = torch.randn(4)
    beta = torch.randn(4)
    result = solve(x, gamma, beta, eps=1e-5)
    expected = F.layer_norm(x, (4,), weight=gamma, bias=beta, eps=1e-5)
    assert torch.allclose(result, expected, atol=1e-5)

def test_eps(solve):
    torch.manual_seed(2)
    x = torch.randn(2, 4)
    gamma = torch.ones(4)
    beta = torch.zeros(4)
    eps = 1e-3
    result = solve(x, gamma, beta, eps=eps)
    expected = F.layer_norm(x, (4,), weight=gamma, bias=beta, eps=eps)
    assert torch.allclose(result, expected, atol=1e-5)

def test_default_eps(solve):
    # test that default eps is 1e-5
    import inspect
    sig = inspect.signature(solve)
    assert sig.parameters['eps'].default == 1e-5, "Default eps should be 1e-5"
    torch.manual_seed(3)
    x = torch.randn(2, 3)
    gamma = torch.randn(3)
    beta = torch.randn(3)
    result = solve(x, gamma, beta)
    expected = F.layer_norm(x, (3,), weight=gamma, bias=beta, eps=1e-5)
    assert torch.allclose(result, expected, atol=1e-5)

TESTS = [test_example, test_gamma_beta, test_random_2d, test_3d, test_eps, test_default_eps]

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
    print("All tests passed for layer-norm")
