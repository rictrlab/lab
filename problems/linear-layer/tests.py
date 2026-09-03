import torch
import torch.nn.functional as F

def test_example(solve):
    x = torch.tensor([[1., 2., 3.]])
    weight = torch.tensor([[1., 0., 0.], [0., 1., 0.]])
    bias = torch.tensor([10., 20.])
    result = solve(x, weight, bias)
    expected = torch.tensor([[11., 22.]])
    assert torch.allclose(result, expected)

def test_random(solve):
    torch.manual_seed(0)
    x = torch.randn(4, 3)
    weight = torch.randn(5, 3)
    bias = torch.randn(5)
    result = solve(x, weight, bias)
    expected = F.linear(x, weight, bias)
    assert torch.allclose(result, expected, atol=1e-5)

def test_batched(solve):
    torch.manual_seed(1)
    x = torch.randn(2, 3, 4)
    weight = torch.randn(6, 4)
    bias = torch.randn(6)
    result = solve(x, weight, bias)
    expected = F.linear(x, weight, bias)
    assert torch.allclose(result, expected, atol=1e-5)
    assert result.shape == torch.Size([2, 3, 6])

def test_single(solve):
    x = torch.randn(1, 2)
    weight = torch.randn(1, 2)
    bias = torch.randn(1)
    result = solve(x, weight, bias)
    expected = F.linear(x, weight, bias)
    assert torch.allclose(result, expected, atol=1e-5)

def test_no_broadcast_error(solve):
    # bias should broadcast correctly over batch
    x = torch.zeros(2, 3)
    weight = torch.eye(3)
    bias = torch.tensor([1., 2., 3.])
    result = solve(x, weight, bias)
    expected = torch.tensor([[1., 2., 3.], [1., 2., 3.]])
    assert torch.allclose(result, expected)

TESTS = [test_example, test_random, test_batched, test_single, test_no_broadcast_error]

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
    print("All tests passed for linear-layer")
