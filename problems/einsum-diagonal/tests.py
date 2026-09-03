import torch

def test_3x3(solve):
    x = torch.tensor([[1, 2, 3],
                      [4, 5, 6],
                      [7, 8, 9]])
    result = solve(x)
    expected = torch.tensor([1, 5, 9])
    assert torch.equal(result, expected), f"Expected {expected}, got {result}"

def test_2x2_float(solve):
    x = torch.tensor([[10., 20.],
                      [30., 40.]])
    result = solve(x)
    expected = torch.tensor([10., 40.])
    assert torch.allclose(result, expected)

def test_1x1(solve):
    x = torch.tensor([[99.]])
    result = solve(x)
    expected = torch.tensor([99.])
    assert torch.equal(result, expected) or torch.allclose(result, expected)

def test_identity(solve):
    x = torch.eye(4)
    result = solve(x)
    expected = torch.ones(4)
    assert torch.allclose(result, expected)

def test_random(solve):
    torch.manual_seed(0)
    x = torch.randn(5, 5)
    result = solve(x)
    expected = torch.diagonal(x)
    # einsum returns contiguous, diagonal may be non-contiguous but values equal
    assert torch.allclose(result, expected), f"Expected {expected}, got {result}"
    assert result.shape == torch.Size([5])

TESTS = [test_3x3, test_2x2_float, test_1x1, test_identity, test_random]

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
    print("All tests passed for einsum-diagonal")
