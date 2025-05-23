"""
Port allocation utilities for avoiding port conflicts
Critical for Windows development where port 8000/8001 conflicts are common
"""
import socket
import random
import contextlib
from typing import Optional, List


def pick_free_port(start: int = 8100, end: int = 9000, exclude: Optional[List[int]] = None) -> int:
    """
    Find an available TCP port for local development.
    
    This utility helps avoid the common Windows error:
    [Errno 10048] Address already in use
    
    Args:
        start (int): Starting port number to check. Defaults to 8100.
        end (int): Ending port number to check. Defaults to 9000.
        exclude (List[int], optional): List of ports to skip even if available.
    
    Returns:
        int: An available port number.
    
    Raises:
        RuntimeError: If no free port found after maximum attempts.
    
    Example:
        >>> port = pick_free_port()
        >>> print(f"Starting server on port {port}")
        Starting server on port 8147
    """
    exclude = exclude or []
    max_attempts = 50
    
    for _ in range(max_attempts):
        port = random.randint(start, end)
        
        if port in exclude:
            continue
            
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            try:
                sock.bind(('127.0.0.1', port))
                # Port is available
                return port
            except socket.error:
                # Port is in use, try another
                continue
    
    raise RuntimeError(f"No free port found between {start} and {end} after {max_attempts} attempts")


def is_port_available(port: int, host: str = '127.0.0.1') -> bool:
    """
    Check if a specific port is available.
    
    Args:
        port (int): Port number to check.
        host (str): Host address to check. Defaults to localhost.
    
    Returns:
        bool: True if port is available, False otherwise.
    """
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        try:
            sock.bind((host, port))
            return True
        except socket.error:
            return False


def get_adk_ports() -> dict:
    """
    Get recommended ports for ADK services with fallbacks.
    
    Returns:
        dict: Dictionary with service names and allocated ports.
              Keys: 'adk_web', 'api_server', 'live_gateway'
    
    Example:
        >>> ports = get_adk_ports()
        >>> print(ports)
        {'adk_web': 8000, 'api_server': 8001, 'live_gateway': 8002}
    """
    ports = {}
    
    # Try default ADK web port first
    if is_port_available(8000):
        ports['adk_web'] = 8000
    else:
        ports['adk_web'] = pick_free_port(8100, 8200)
    
    # API server port
    if is_port_available(8001):
        ports['api_server'] = 8001
    else:
        ports['api_server'] = pick_free_port(8201, 8300, exclude=[ports['adk_web']])
    
    # Live gateway port
    if is_port_available(8002):
        ports['live_gateway'] = 8002
    else:
        ports['live_gateway'] = pick_free_port(8301, 8400, 
                                              exclude=[ports['adk_web'], ports['api_server']])
    
    return ports


if __name__ == "__main__":
    # Quick test when run directly
    print("Checking port availability...")
    ports = get_adk_ports()
    print(f"Recommended ports:")
    for service, port in ports.items():
        print(f"  {service}: {port}")
