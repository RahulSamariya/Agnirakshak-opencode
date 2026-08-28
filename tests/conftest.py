"""Test configuration and fixtures."""
import sys
from pathlib import Path

# Add project root to Python path for all test modules
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Add apps/api to path for API tests
API_DIR = PROJECT_ROOT / "apps" / "api"
if API_DIR.exists() and str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

# Add apps/worker to path for worker tests
WORKER_DIR = PROJECT_ROOT / "apps" / "worker"
if WORKER_DIR.exists() and str(WORKER_DIR) not in sys.path:
    sys.path.insert(0, str(WORKER_DIR))
