import torch

def test_example_float(solve):
    a = torch.tensor([1., 2., 3.])
    b = torch.tensor([4., 5.])
    result = solve(a, b)
    expected = torch.tensor([[4., 5.], [8., 10.], [12., 15.]])
    assert result.shape == torch.Size([3, 2])
    assert torch.allclose(result, expected)

def test_int(solve):
    a = torch.tensor([1, 2])
    b = torch.tensor([3, 4, 5])
    result = solve(a, b)
    expected = torch.tensor([[3, 4, 5], [6, 8, 10]])
    assert torch.equal(result, expected)

def test_single_element(solve):
    a = torch.tensor([2.])
    b = torch.tensor([3.])
    result = solve(a, b)
    expected = torch.tensor([[6.]])
    assert torch.allclose(result, expected)

def test_random(solve):
    torch.manual_seed(0)
    a = torch.randn(4)
    b = torch.randn(3)
    result = solve(a, b)
    expected = torch.outer(a, b)
    assert torch.allclose(result, expected)

def test_zeros(solve):
    a = torch.zeros(2)
    b = torch.randn(3)
    result = solve(a, b)
    expected = torch.zeros(2, 3)
    assert torch.allclose(result, expected)

TESTS = [test_example_float, test_int, test_single_element, test_random, test_zeros]

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
    print("All tests passed for outer-product")
