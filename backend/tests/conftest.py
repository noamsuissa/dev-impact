"""
Pytest configuration for backend tests
"""
import sys
from pathlib import Path

# Add the parent directory to Python path so we can import 'backend'
backend_dir = Path(__file__).parent.parent
parent_dir = backend_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

