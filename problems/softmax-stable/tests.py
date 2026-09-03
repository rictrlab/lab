import torch
import torch.nn.functional as F

def test_example(solve):
    x = torch.tensor([1., 2., 3.])
    result = solve(x)
    expected = torch.softmax(x, dim=-1)
    assert torch.allclose(result, expected, atol=1e-5)
    assert torch.allclose(result.sum(), torch.tensor(1.0), atol=1e-5)

def test_large_values(solve):
    x = torch.tensor([1000., 1000., 1000.])
    result = solve(x)
    expected = torch.tensor([0.33333334, 0.33333334, 0.33333334])
    assert torch.allclose(result, expected, atol=1e-5)
    assert not torch.isnan(result).any(), "Result contains NaN, not stable"
    assert not torch.isinf(result).any(), "Result contains Inf"

def test_2d(solve):
    x = torch.tensor([[1., 2., 3.], [1., 1., 1.]])
    result = solve(x)
    expected = torch.softmax(x, dim=-1)
    assert torch.allclose(result, expected, atol=1e-5)
    # each row sums to 1
    assert torch.allclose(result.sum(dim=-1), torch.ones(2), atol=1e-5)

def test_random(solve):
    torch.manual_seed(0)
    x = torch.randn(2, 3, 4)
    result = solve(x)
    expected = torch.softmax(x, dim=-1)
    assert torch.allclose(result, expected, atol=1e-5)
    # check sums
    assert torch.allclose(result.sum(dim=-1), torch.ones(2, 3), atol=1e-5)

def test_negative_large(solve):
    x = torch.tensor([-1000., 0., 1000.])
    result = solve(x)
    # should be stable, first element ~0, last ~1
    assert torch.allclose(result.sum(), torch.tensor(1.0), atol=1e-5)
    assert result[0].item() < 1e-6
    assert result[2].item() > 0.999
    assert not torch.isnan(result).any()

def test_single_element(solve):
    x = torch.tensor([5.])
    result = solve(x)
    expected = torch.tensor([1.])
    assert torch.allclose(result, expected)

TESTS = [test_example, test_large_values, test_2d, test_random, test_negative_large, test_single_element]

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
    print("All tests passed for softmax-stable")
