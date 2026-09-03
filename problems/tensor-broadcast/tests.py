import torch

def test_example(solve):
    a = torch.tensor([[1.], [2.], [3.]])
    b = torch.tensor([[10., 20., 30., 40.]])
    result = solve(a, b)
    expected = torch.tensor([[11., 21., 31., 41.],
                             [12., 22., 32., 42.],
                             [13., 23., 33., 43.]])
    assert result.shape == torch.Size([3, 4]), f"Expected shape (3,4), got {tuple(result.shape)}"
    assert torch.allclose(result, expected), f"Expected\n{expected}\nGot\n{result}"

def test_random(solve):
    torch.manual_seed(0)
    a = torch.randn(3, 1)
    b = torch.randn(1, 4)
    result = solve(a, b)
    expected = a + b
    assert torch.allclose(result, expected), f"Broadcast mismatch\nExpected {expected}\nGot {result}"

def test_int_tensors(solve):
    a = torch.tensor([[1], [2], [3]])
    b = torch.tensor([[10, 20, 30, 40]])
    result = solve(a, b)
    expected = a + b
    assert torch.equal(result, expected)

def test_zeros(solve):
    a = torch.zeros(3, 1)
    b = torch.zeros(1, 4)
    result = solve(a, b)
    assert torch.equal(result, torch.zeros(3, 4))

TESTS = [test_example, test_random, test_int_tensors, test_zeros]

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
    print("All tests passed for tensor-broadcast")
