"""
Unit tests for utility functions.
"""

import unittest
from unittest.mock import patch, Mock
from utils.helpers import (
    get_my_public_ip,
    print_section,
    print_resource_info,
    print_error,
    print_success,
    wait_with_progress
)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility helper functions."""
    
    @patch('requests.get')
    def test_get_my_public_ip_success(self, mock_get):
        """Test successful public IP retrieval."""
        mock_response = Mock()
        mock_response.text = "203.0.113.1"
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        ip = get_my_public_ip()
        
        self.assertEqual(ip, "203.0.113.1")
        mock_get.assert_called_once()
    
    @patch('utils.helpers.requests')
    def test_get_my_public_ip_failure(self, mock_requests):
        """Test public IP retrieval failure."""
        import requests as real_requests
        # Make RequestException available
        mock_requests.RequestException = real_requests.RequestException
        mock_requests.get.side_effect = real_requests.RequestException("Network error")
        
        ip = get_my_public_ip()
        
        self.assertIsNone(ip)
    
    @patch('builtins.print')
    def test_print_section(self, mock_print):
        """Test print_section function."""
        print_section("Test Section")
        
        # Verify print was called
        self.assertTrue(mock_print.called)
        # Check that the section title is in one of the calls
        call_args = [str(call[0]) for call in mock_print.call_args_list]
        self.assertTrue(any("Test Section" in arg for arg in call_args))
    
    @patch('builtins.print')
    def test_print_resource_info(self, mock_print):
        """Test print_resource_info function."""
        print_resource_info("Resource", "resource-name", "resource-id-123")
        
        self.assertTrue(mock_print.called)
    
    @patch('builtins.print')
    def test_print_error(self, mock_print):
        """Test print_error function."""
        print_error("Test error message")
        
        self.assertTrue(mock_print.called)
        # Verify error symbol or message appears
        call_args = [str(call[0]) for call in mock_print.call_args_list]
        self.assertTrue(any("error" in arg.lower() or "✗" in arg for arg in call_args))
    
    @patch('builtins.print')
    def test_print_success(self, mock_print):
        """Test print_success function."""
        print_success("Test success message")
        
        self.assertTrue(mock_print.called)
        # Verify success symbol or message appears
        call_args = [str(call[0]) for call in mock_print.call_args_list]
        self.assertTrue(any("success" in arg.lower() or "✓" in arg for arg in call_args))
    
    @patch('time.sleep')
    @patch('builtins.print')
    def test_wait_with_progress(self, mock_print, mock_sleep):
        """Test wait_with_progress function."""
        wait_with_progress("Testing", 2)
        
        # Verify sleep was called
        self.assertTrue(mock_sleep.called)
        # Verify print was called
        self.assertTrue(mock_print.called)


class TestUtilityInputValidation(unittest.TestCase):
    """Test input validation in utility functions."""
    
    def test_print_section_with_empty_string(self):
        """Test print_section with empty string."""
        try:
            print_section("")
        except Exception as e:
            self.fail(f"print_section raised {e} unexpectedly")
    
    def test_print_resource_info_with_none(self):
        """Test print_resource_info with None values."""
        try:
            print_resource_info(None, None, None)
        except Exception as e:
            self.fail(f"print_resource_info raised {e} unexpectedly")
    
    @patch('builtins.print')
    def test_print_error_with_various_types(self, mock_print):
        """Test print_error with various input types."""
        test_inputs = ["string error", 123, None, {"error": "dict"}]
        
        for test_input in test_inputs:
            try:
                print_error(test_input)
            except Exception as e:
                self.fail(f"print_error raised {e} for input {test_input}")


if __name__ == "__main__":
    unittest.main()
