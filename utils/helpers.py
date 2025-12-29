"""
Helper utilities for AWS operations.
"""

import requests
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def get_my_public_ip() -> Optional[str]:
    """
    Get the public IP address of the machine running this script.
    
    Returns:
        str: Public IP address or None if unable to retrieve
    """
    try:
        response = requests.get('https://checkip.amazonaws.com', timeout=5)
        response.raise_for_status()
        ip = response.text.strip()
        logger.info(f"Retrieved public IP: {ip}")
        return ip
    except requests.RequestException as e:
        logger.error(f"Failed to retrieve public IP: {e}")
        return None


def format_tags(tags: list) -> list:
    """
    Format tags for AWS resources.
    
    Args:
        tags: List of tag dictionaries
        
    Returns:
        list: Formatted tags
    """
    return [{"Key": tag["Key"], "Value": tag["Value"]} for tag in tags]


def print_section(title: str, width: int = 60) -> None:
    """
    Print a formatted section header.
    
    Args:
        title: Section title
        width: Width of the separator line
    """
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)


def print_resource_info(resource_type: str, resource_name: str, resource_id: str) -> None:
    """
    Print formatted resource information.
    
    Args:
        resource_type: Type of AWS resource
        resource_name: Name of the resource
        resource_id: AWS resource ID
    """
    print(f"✓ {resource_type}: {resource_name}")
    print(f"  ID: {resource_id}")


def print_error(message: str) -> None:
    """
    Print formatted error message.
    
    Args:
        message: Error message to display
    """
    print(f"✗ ERROR: {message}")


def print_success(message: str) -> None:
    """
    Print formatted success message.
    
    Args:
        message: Success message to display
    """
    print(f"✓ {message}")


def wait_with_progress(message: str, seconds: int = 30) -> None:
    """
    Display a waiting message with progress indicator.
    
    Args:
        message: Message to display
        seconds: Number of seconds to wait
    """
    import time
    import sys
    
    print(f"\n{message}", end="", flush=True)
    for i in range(seconds):
        time.sleep(1)
        print(".", end="", flush=True)
    print(" Done!")
