#!/usr/bin/env python3
"""
Token Generation System for Private Resume URLs

This module provides cryptographically secure token generation for creating
private, shareable resume URLs. Tokens are generated using Python's secrets
module to ensure unpredictability and security.

Usage:
    python generate_token.py [--length LENGTH] [--output FILE] [--no-write]

Examples:
    python generate_token.py                    # Generate 10-char token, save to resume_token.txt
    python generate_token.py --length 12       # Generate 12-char token
    python generate_token.py --no-write        # Print token without saving
    python generate_token.py --output my.txt   # Save to custom file

Token Specifications:
    - Length: 8-12 characters (default: 10)
    - Character set: a-z, A-Z, 0-9 (62 possible characters)
    - Entropy: ~59.5 bits for 10 characters
    - Collision probability: < 0.0001% for reasonable usage

Author: Resume Builder System
"""

import argparse
import math
import secrets
import string
import sys
from pathlib import Path
from typing import Optional


def generate_token(length: int = 10) -> str:
    """
    Generate a cryptographically secure random token.

    Uses Python's secrets module which provides access to the most secure
    source of randomness available on the system (typically /dev/urandom
    on Unix systems or CryptGenRandom on Windows).

    Args:
        length: The desired length of the token (8-12 characters).
                Default is 10 characters.

    Returns:
        A random string of the specified length containing only
        alphanumeric characters (a-z, A-Z, 0-9).

    Raises:
        ValueError: If length is not between 8 and 12 characters.

    Example:
        >>> token = generate_token(10)
        >>> len(token)
        10
        >>> all(c in string.ascii_letters + string.digits for c in token)
        True
    """
    if not 8 <= length <= 12:
        raise ValueError(f"Token length must be between 8 and 12 characters, got {length}")

    # Define the character set: a-z, A-Z, 0-9
    alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits

    # Generate the token using secrets.choice for each character
    token = ''.join(secrets.choice(alphabet) for _ in range(length))

    return token


def write_token_to_file(token: str, filepath: Optional[str] = None) -> str:
    """
    Write a token to a file.

    Writes the token to the specified file path, or to the default
    resume_token.txt in the project root directory.

    Args:
        token: The token string to write.
        filepath: Optional path to the output file. If not provided,
                  defaults to 'resume_token.txt' in the project root.

    Returns:
        The absolute path to the file where the token was written.

    Example:
        >>> path = write_token_to_file("abc123xyz")
        >>> Path(path).exists()
        True
    """
    if filepath is None:
        # Default to project root's resume_token.txt
        project_root = Path(__file__).parent.parent
        filepath = project_root / "resume_token.txt"
    else:
        filepath = Path(filepath)

    # Ensure parent directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Write the token
    with open(filepath, 'w') as f:
        f.write(token + '\n')

    return str(filepath.resolve())


def read_existing_token(filepath: Optional[str] = None) -> Optional[str]:
    """
    Read an existing token from a file.

    Args:
        filepath: Optional path to the token file. If not provided,
                  defaults to 'resume_token.txt' in the project root.

    Returns:
        The token string if the file exists and is readable, None otherwise.
    """
    if filepath is None:
        project_root = Path(__file__).parent.parent
        filepath = project_root / "resume_token.txt"
    else:
        filepath = Path(filepath)

    try:
        with open(filepath, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def calculate_collision_probability(token_length: int, num_tokens: int) -> float:
    """
    Calculate the approximate collision probability for a given number of tokens.

    Uses the birthday problem approximation to estimate the probability of
    at least one collision among num_tokens tokens of the given length.

    Args:
        token_length: The length of each token.
        num_tokens: The number of tokens to consider.

    Returns:
        The approximate probability of at least one collision (0.0 to 1.0).

    Example:
        >>> prob = calculate_collision_probability(10, 10000)
        >>> prob < 0.000001  # Very low collision probability
        True
    """
    # Total possible tokens with 62 characters (a-z, A-Z, 0-9)
    total_possible = 62 ** token_length

    # Birthday problem approximation: p ~ 1 - e^(-n^2 / 2m)
    # where n = num_tokens, m = total_possible
    exponent = -(num_tokens ** 2) / (2 * total_possible)
    probability = 1 - math.exp(exponent)

    return probability


def verify_uniqueness(length: int = 10, num_tokens: int = 10000) -> bool:
    """
    Verify that token generation produces unique tokens.

    Generates a specified number of tokens and checks for duplicates.
    This is useful for testing the quality of the random generation.

    Args:
        length: The length of tokens to generate.
        num_tokens: The number of tokens to generate for testing.

    Returns:
        True if all generated tokens are unique, False otherwise.

    Note:
        This function is primarily for testing purposes. In production,
        the collision probability is so low that checking isn't necessary
        for reasonable numbers of tokens.
    """
    tokens = set()
    for _ in range(num_tokens):
        token = generate_token(length)
        if token in tokens:
            return False
        tokens.add(token)
    return True


def main() -> int:
    """
    Main entry point for the token generation CLI.

    Parses command-line arguments and generates a token according to
    the specified options.

    Returns:
        int: Exit code (0 for success, non-zero for errors).
    """
    parser = argparse.ArgumentParser(
        description="Generate cryptographically secure tokens for private resume URLs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                      Generate a 10-character token and save it
  %(prog)s --length 12          Generate a 12-character token
  %(prog)s --no-write           Print token without saving to file
  %(prog)s --output custom.txt  Save token to a custom file
  %(prog)s --verify             Verify uniqueness with 10,000 tokens

Token Security:
  - Uses Python's secrets module (cryptographically secure)
  - Character set: a-z, A-Z, 0-9 (62 characters)
  - 10-character token has ~59.5 bits of entropy
  - Collision probability < 0.0001%% for 10,000 tokens
        """
    )

    parser.add_argument(
        '--length', '-l',
        type=int,
        default=10,
        choices=range(8, 13),
        metavar='LENGTH',
        help='Token length in characters (8-12, default: 10)'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Output file path (default: resume_token.txt in project root)'
    )

    parser.add_argument(
        '--no-write', '-n',
        action='store_true',
        help='Print token to stdout without writing to file'
    )

    parser.add_argument(
        '--verify', '-v',
        action='store_true',
        help='Run uniqueness verification (generates 10,000 tokens)'
    )

    parser.add_argument(
        '--show-existing', '-s',
        action='store_true',
        help='Show existing token if present'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show token statistics and collision probability'
    )

    args = parser.parse_args()

    # Show existing token if requested
    if args.show_existing:
        existing = read_existing_token(args.output)
        if existing:
            print(f"Existing token: {existing}")
        else:
            print("No existing token found.")
        return 0

    # Run verification if requested
    if args.verify:
        print(f"Verifying uniqueness with 10,000 {args.length}-character tokens...")
        if verify_uniqueness(args.length, 10000):
            print("SUCCESS: All 10,000 tokens were unique.")
            collision_prob = calculate_collision_probability(args.length, 10000)
            print(f"Theoretical collision probability: {collision_prob:.10f}")
            return 0
        else:
            print("FAILURE: Duplicate token detected!")
            return 1

    # Show statistics if requested
    if args.stats:
        total_possible = 62 ** args.length
        entropy_bits = args.length * math.log2(62)  # total entropy in bits
        collision_prob_10k = calculate_collision_probability(args.length, 10000)
        collision_prob_1m = calculate_collision_probability(args.length, 1000000)

        print(f"Token Statistics for {args.length}-character tokens:")
        print(f"  Character set: a-z, A-Z, 0-9 (62 characters)")
        print(f"  Total possible tokens: {total_possible:,}")
        print(f"  Entropy: {entropy_bits:.1f} bits")
        print(f"  Collision probability (10,000 tokens): {collision_prob_10k:.10%}")
        print(f"  Collision probability (1,000,000 tokens): {collision_prob_1m:.10%}")
        return 0

    # Generate token
    try:
        token = generate_token(args.length)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Output the token
    if args.no_write:
        print(token)
    else:
        filepath = write_token_to_file(token, args.output)
        print(f"Generated token: {token}")
        print(f"Token saved to: {filepath}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
