import pytest
import sys
import os

# Add the project root to sys.path so we can import scripts.demo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from scripts import demo

def test_check_backend_ready_timeout(monkeypatch):
    """Test that check_backend_ready times out gracefully."""
    import urllib.request
    
    # Mock urlopen to raise an exception, simulating backend being down
    def mock_urlopen(*args, **kwargs):
        raise urllib.error.URLError("Connection refused")
        
    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)
    
    # Mock time.sleep to avoid actually waiting during the test
    monkeypatch.setattr(demo.time, "sleep", lambda x: None)
    
    result = demo.check_backend_ready()
    assert result is False

def test_check_backend_ready_success(monkeypatch):
    """Test that check_backend_ready returns True when backend is up."""
    import urllib.request
    
    class MockResponse:
        def getcode(self):
            return 200
            
    # Mock urlopen to succeed immediately
    def mock_urlopen(*args, **kwargs):
        return MockResponse()
        
    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)
    monkeypatch.setattr(demo.time, "sleep", lambda x: None)
    
    result = demo.check_backend_ready()
    assert result is True
