#!/usr/bin/env python3
"""
Token Intelligence API Server
Main entry point for running the Token Intelligence API server.
"""

import os
import argparse
from token_intelligence.api import start_server
from token_intelligence.utils.logging import setup_file_logging, set_log_level, get_logger


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Token Intelligence API Server')
    
    parser.add_argument('--host', default='0.0.0.0',
                        help='Host to bind the server to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port to run the server on (default: 5000)')
    parser.add_argument('--debug', action='store_true',
                        help='Run in debug mode')
    parser.add_argument('--log-level', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Log level (default: INFO)')
    parser.add_argument('--log-dir', default='./logs',
                        help='Directory for log files (default: ./logs)')
    
    return parser.parse_args()


def main():
    """Main entry point for the API server."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Set up logging
    setup_file_logging(args.log_dir, args.log_level)
    set_log_level(args.log_level)
    logger = get_logger(__name__)
    
    # Log startup information
    logger.info(f"Starting Token Intelligence API Server v{os.environ.get('TOKEN_INTELLIGENCE_VERSION', '1.0.0')}")
    logger.info(f"Host: {args.host}, Port: {args.port}, Debug: {args.debug}")
    
    # Start the server
    start_server(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main() 