import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--visual", 
        action="store_true", 
        default=False, 
        help="Run tests in visual mode (disable headless)"
    )

@pytest.fixture
def visual_mode(request):
    return request.config.getoption("--visual")