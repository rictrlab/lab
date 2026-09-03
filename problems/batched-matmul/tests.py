import torch

def test_example(solve):
    a = torch.tensor([[[1., 2.], [3., 4.]]])
    b = torch.tensor([[[5., 6.], [7., 8.]]])
    result = solve(a, b)
    expected = torch.tensor([[[19., 22.], [43., 50.]]])
    assert result.shape == torch.Size([1, 2, 2])
    assert torch.allclose(result, expected)

def test_random(solve):
    torch.manual_seed(0)
    a = torch.randn(2, 3, 4)
    b = torch.randn(2, 4, 5)
    result = solve(a, b)
    expected = torch.bmm(a, b)
    assert result.shape == expected.shape
    assert torch.allclose(result, expected, atol=1e-5)

def test_larger_batch(solve):
    torch.manual_seed(42)
    a = torch.randn(4, 2, 3)
    b = torch.randn(4, 3, 6)
    result = solve(a, b)
    expected = torch.bmm(a, b)
    assert torch.allclose(result, expected, atol=1e-5)

def test_single_element(solve):
    a = torch.randn(1, 1, 1)
    b = torch.randn(1, 1, 1)
    result = solve(a, b)
    expected = torch.bmm(a, b)
    assert torch.allclose(result, expected)

def test_bmm_vs_matmul(solve):
    torch.manual_seed(123)
    a = torch.randn(3, 5, 7)
    b = torch.randn(3, 7, 2)
    result = solve(a, b)
    # also valid to compare with matmul
    expected = torch.matmul(a, b)
    assert torch.allclose(result, expected)

TESTS = [test_example, test_random, test_larger_batch, test_single_element, test_bmm_vs_matmul]

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
    print("All tests passed for batched-matmul")
