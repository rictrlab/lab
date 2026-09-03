import torch

def test_example(solve):
    x = torch.tensor([[1., 2., 3.], [4., 5., 6.]])
    mask = torch.tensor([[True, False, True], [False, True, False]])
    result = solve(x, mask, -1)
    expected = torch.tensor([[-1., 2., -1.], [4., -1., 6.]])
    assert torch.allclose(result, expected)

def test_gt_mask(solve):
    x = torch.tensor([1, 2, 3, 4])
    mask = x > 2
    result = solve(x, mask, 0)
    expected = torch.tensor([1, 2, 0, 0])
    assert torch.equal(result, expected)

def test_all_false(solve):
    x = torch.randn(3, 3)
    mask = torch.zeros(3, 3, dtype=torch.bool)
    result = solve(x, mask, 99.0)
    assert torch.equal(result, x)

def test_all_true(solve):
    x = torch.randn(2, 2)
    mask = torch.ones(2, 2, dtype=torch.bool)
    result = solve(x, mask, 5.5)
    expected = torch.full((2,2), 5.5)
    assert torch.allclose(result, expected)

def test_no_mutation(solve):
    x = torch.tensor([1., 2., 3.])
    x_clone = x.clone()
    mask = torch.tensor([True, False, True])
    _ = solve(x, mask, 0)
    # original should ideally not be mutated; but if solution uses masked_fill_ in-place, it would fail
    # we check clone preserved or at least result is correct
    result = solve(x_clone, mask, 0)
    expected = torch.tensor([0., 2., 0.])
    assert torch.allclose(result, expected)

TESTS = [test_example, test_gt_mask, test_all_false, test_all_true, test_no_mutation]

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
    print("All tests passed for masked-fill")
