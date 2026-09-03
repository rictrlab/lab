import torch

def test_example1(solve):
    x = torch.tensor([[3., 4.], [1., 2.]])
    result = solve(x)
    expected = x / x.norm(dim=1, keepdim=True)
    assert result.shape == x.shape
    assert torch.allclose(result, expected, atol=1e-5)
    # norms should be 1
    norms = result.norm(dim=1)
    assert torch.allclose(norms, torch.ones_like(norms), atol=1e-5)

def test_single_row(solve):
    x = torch.tensor([[1., 1., 1.]])
    result = solve(x)
    expected = torch.tensor([[0.57735026919, 0.57735026919, 0.57735026919]])
    assert torch.allclose(result, expected, atol=1e-5)

def test_random(solve):
    torch.manual_seed(0)
    x = torch.randn(4, 5)
    # ensure non-zero rows (randn already non-zero with high prob)
    result = solve(x)
    expected = x / torch.norm(x, p=2, dim=1, keepdim=True)
    assert torch.allclose(result, expected, atol=1e-5)
    norms = torch.norm(result, p=2, dim=1)
    assert torch.allclose(norms, torch.ones(4), atol=1e-5)

def test_already_normalized(solve):
    x = torch.tensor([[1., 0., 0.], [0., 1., 0.]])
    result = solve(x)
    assert torch.allclose(result, x, atol=1e-5)

def test_preserves_direction(solve):
    x = torch.tensor([[2., 0.], [0., 5.]])
    result = solve(x)
    # direction should be same, first row positive x only
    assert torch.allclose(result[0], torch.tensor([1., 0.]), atol=1e-5)
    assert torch.allclose(result[1], torch.tensor([0., 1.]), atol=1e-5)

TESTS = [test_example1, test_single_row, test_random, test_already_normalized, test_preserves_direction]

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
    print("All tests passed for normalized-rows")
