import torch

def test_example(solve):
    x = torch.tensor([0., 1., -1.])
    result = solve(x)
    expected = x * torch.sigmoid(x)
    assert torch.allclose(result, expected, atol=1e-5)
    # manual check
    assert abs(result[0].item() - 0.0) < 1e-5
    assert abs(result[1].item() - 0.7310586) < 1e-4
    assert abs(result[2].item() - (-0.2689414)) < 1e-4

def test_scalar(solve):
    x = torch.tensor([2.])
    result = solve(x)
    expected = torch.tensor([1.7615941559557649])
    assert torch.allclose(result, expected, atol=1e-5)

def test_random(solve):
    torch.manual_seed(0)
    x = torch.randn(3, 4)
    result = solve(x)
    expected = x * torch.sigmoid(x)
    assert torch.allclose(result, expected, atol=1e-5)

def test_zero(solve):
    x = torch.zeros(5)
    result = solve(x)
    expected = torch.zeros(5)
    assert torch.allclose(result, expected)

def test_grad(solve):
    x = torch.tensor([1.0], requires_grad=True)
    y = solve(x)
    y.sum().backward()
    assert x.grad is not None
    # grad should be non-zero and finite
    assert torch.isfinite(x.grad).all()
    assert x.grad.item() != 0

TESTS = [test_example, test_scalar, test_random, test_zero, test_grad]

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
    print("All tests passed for custom-activation")
