import torch

def test_basic(solve):
    result = solve()
    assert isinstance(result, torch.Tensor), f"Expected torch.Tensor, got {type(result)}"
    assert result.shape == torch.Size([3, 3]), f"Expected shape (3,3), got {tuple(result.shape)}"
    expected = torch.arange(9).reshape(3, 3)
    assert torch.equal(result, expected), f"Expected\n{expected}\nGot\n{result}"

def test_dtype(solve):
    result = solve()
    expected = torch.arange(9).reshape(3, 3)
    assert result.dtype == expected.dtype, f"Expected dtype {expected.dtype}, got {result.dtype}"

def test_values(solve):
    result = solve()
    assert result[0, 0].item() == 0
    assert result[1, 1].item() == 4
    assert result[2, 2].item() == 8
    assert result.sum().item() == 36
    assert result[0, 2].item() == 2
    assert result[2, 0].item() == 6

def test_no_args(solve):
    import inspect
    sig = inspect.signature(solve)
    assert len(sig.parameters) == 0, f"solve() should take no arguments, got {list(sig.parameters.keys())}"

TESTS = [test_basic, test_dtype, test_values, test_no_args]

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
    print("All tests passed for tensor-creation")
