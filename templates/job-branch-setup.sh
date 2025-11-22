#!/bin/bash
#
# Job Branch Setup Script for Resume Builder
#
# This script automates the creation of job application branches with all required files.
# It creates a new branch with the naming convention resume/{job-name}, sets up the
# active profile, and generates a unique resume token.
#
# Usage:
#   ./templates/job-branch-setup.sh <job-name> <profile-name>
#
# Examples:
#   ./templates/job-branch-setup.sh aws-security-eng leadership
#   ./templates/job-branch-setup.sh google-sre technical
#   ./templates/job-branch-setup.sh startup-devops default
#
# Arguments:
#   job-name     - Name for the job branch (alphanumeric and hyphens only)
#   profile-name - Name of the profile to use (must exist in resume_builder/profiles/)
#
# Created files:
#   - resume_builder/active_profile.txt  (contains the profile name)
#   - resume_builder/resume_token.txt    (contains a unique token)
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory (for finding project root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

#######################################
# Print an error message and exit
# Arguments:
#   Error message to display
#######################################
error_exit() {
    echo -e "${RED}ERROR: $1${NC}" >&2
    exit 1
}

#######################################
# Print a success message
# Arguments:
#   Success message to display
#######################################
success_msg() {
    echo -e "${GREEN}$1${NC}"
}

#######################################
# Print an info message
# Arguments:
#   Info message to display
#######################################
info_msg() {
    echo -e "${BLUE}$1${NC}"
}

#######################################
# Print a warning message
# Arguments:
#   Warning message to display
#######################################
warn_msg() {
    echo -e "${YELLOW}$1${NC}"
}

#######################################
# Display usage information
#######################################
usage() {
    echo "Usage: $0 <job-name> <profile-name>"
    echo ""
    echo "Create a new job application branch with all required files."
    echo ""
    echo "Arguments:"
    echo "  job-name      Name for the job branch (alphanumeric and hyphens only)"
    echo "  profile-name  Name of the profile to use"
    echo ""
    echo "Available profiles:"
    list_profiles
    echo ""
    echo "Examples:"
    echo "  $0 aws-security-eng leadership"
    echo "  $0 google-sre technical"
    echo "  $0 startup-devops default"
    exit 1
}

#######################################
# List available profiles
#######################################
list_profiles() {
    local profiles_dir="$PROJECT_ROOT/resume_builder/profiles"
    if [[ -d "$profiles_dir" ]]; then
        for profile in "$profiles_dir"/*.yaml; do
            if [[ -f "$profile" ]]; then
                basename "$profile" .yaml
            fi
        done
    else
        echo "  (no profiles directory found)"
    fi
}

#######################################
# Validate branch name
# Arguments:
#   Branch name to validate
# Returns:
#   0 if valid, 1 if invalid
#######################################
validate_branch_name() {
    local name="$1"

    # Check if empty
    if [[ -z "$name" ]]; then
        error_exit "Job name cannot be empty"
    fi

    # Check length (reasonable limits)
    if [[ ${#name} -lt 3 ]]; then
        error_exit "Job name must be at least 3 characters long"
    fi

    if [[ ${#name} -gt 50 ]]; then
        error_exit "Job name cannot exceed 50 characters"
    fi

    # Check for valid characters (alphanumeric, hyphens, underscores)
    if [[ ! "$name" =~ ^[a-zA-Z0-9][a-zA-Z0-9_-]*[a-zA-Z0-9]$ ]] && [[ ! "$name" =~ ^[a-zA-Z0-9]{3,}$ ]]; then
        # Allow single valid pattern for short names
        if [[ ! "$name" =~ ^[a-zA-Z0-9_-]+$ ]]; then
            error_exit "Job name can only contain letters, numbers, hyphens, and underscores"
        fi
        # Check it doesn't start or end with hyphen/underscore
        if [[ "$name" =~ ^[-_] ]] || [[ "$name" =~ [-_]$ ]]; then
            error_exit "Job name cannot start or end with a hyphen or underscore"
        fi
    fi

    # Check for consecutive hyphens or underscores
    if [[ "$name" =~ (--|__) ]]; then
        error_exit "Job name cannot contain consecutive hyphens or underscores"
    fi

    return 0
}

#######################################
# Check if profile exists
# Arguments:
#   Profile name to check
# Returns:
#   0 if exists, 1 if not
#######################################
check_profile_exists() {
    local profile="$1"
    local profile_path="$PROJECT_ROOT/resume_builder/profiles/${profile}.yaml"

    if [[ ! -f "$profile_path" ]]; then
        echo -e "${RED}ERROR: Profile '$profile' not found${NC}" >&2
        echo "" >&2
        echo "Available profiles:" >&2
        list_profiles >&2
        exit 1
    fi

    return 0
}

#######################################
# Generate a random token
# Uses Python's secrets module for cryptographic security
# Arguments:
#   None
# Outputs:
#   Random token string
#######################################
generate_token() {
    # Try to use the Python token generator first
    local token_script="$PROJECT_ROOT/scripts/generate_token.py"
    local token
    local stderr_output
    local exit_code

    if [[ -f "$token_script" ]]; then
        # Capture both stdout and stderr, preserving exit code
        stderr_output=$(mktemp)
        token=$(python3 "$token_script" --no-write 2>"$stderr_output")
        exit_code=$?

        if [[ $exit_code -eq 0 ]] && [[ -n "$token" ]]; then
            rm -f "$stderr_output"
            echo "$token"
            return 0
        else
            # Script failed - log the error and fall back
            if [[ -s "$stderr_output" ]]; then
                warn_msg "  Warning: Token script failed: $(cat "$stderr_output")" >&2
            fi
            rm -f "$stderr_output"
            warn_msg "  Using fallback token generation" >&2
        fi
    fi

    # Fallback: generate token using Python directly
    token=$(python3 -c "
import secrets
import string
alphabet = string.ascii_letters + string.digits
print(''.join(secrets.choice(alphabet) for _ in range(10)))
" 2>&1)
    exit_code=$?

    if [[ $exit_code -ne 0 ]]; then
        error_exit "Failed to generate token: $token"
    fi

    echo "$token"
}

#######################################
# Check if we're in a git repository
#######################################
check_git_repo() {
    if ! git -C "$PROJECT_ROOT" rev-parse --is-inside-work-tree &>/dev/null; then
        error_exit "Not a git repository. Please run this script from within the resume repository."
    fi
}

#######################################
# Check for uncommitted changes
#######################################
check_clean_working_tree() {
    if ! git -C "$PROJECT_ROOT" diff-index --quiet HEAD -- 2>/dev/null; then
        warn_msg "Warning: You have uncommitted changes in your working tree."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            error_exit "Aborted by user"
        fi
    fi
}

#######################################
# Main function
#######################################
main() {
    # Check arguments
    if [[ $# -lt 2 ]]; then
        usage
    fi

    local job_name="$1"
    local profile_name="$2"
    local branch_name="resume/${job_name}"

    echo ""
    info_msg "=== Job Branch Setup ==="
    echo ""

    # Step 1: Validate inputs
    info_msg "Validating inputs..."
    validate_branch_name "$job_name"
    check_profile_exists "$profile_name"
    success_msg "  Job name '$job_name' is valid"
    success_msg "  Profile '$profile_name' exists"

    # Step 2: Check git repository
    info_msg "Checking git repository..."
    check_git_repo
    check_clean_working_tree
    success_msg "  Git repository check passed"

    # Step 3: Check if branch already exists
    if git -C "$PROJECT_ROOT" show-ref --verify --quiet "refs/heads/$branch_name" 2>/dev/null; then
        error_exit "Branch '$branch_name' already exists. Please use a different job name or delete the existing branch."
    fi
    success_msg "  Branch name is available"

    # Step 4: Create new branch
    info_msg "Creating branch '$branch_name'..."
    git -C "$PROJECT_ROOT" checkout -b "$branch_name"
    success_msg "  Branch created successfully"

    # Step 5: Create active_profile.txt
    info_msg "Creating active_profile.txt..."
    local active_profile_path="$PROJECT_ROOT/resume_builder/active_profile.txt"
    echo "$profile_name" > "$active_profile_path"
    success_msg "  Created: resume_builder/active_profile.txt (profile: $profile_name)"

    # Step 6: Generate and save token
    info_msg "Generating resume token..."
    local token
    token=$(generate_token)
    local token_path="$PROJECT_ROOT/resume_builder/resume_token.txt"
    echo "$token" > "$token_path"
    success_msg "  Created: resume_builder/resume_token.txt (token: $token)"

    # Step 7: Stage and commit files
    # Note: We use -f for token file since it's in .gitignore but needed for job branches
    info_msg "Committing changes..."
    git -C "$PROJECT_ROOT" add "$active_profile_path"
    git -C "$PROJECT_ROOT" add -f "$token_path"
    git -C "$PROJECT_ROOT" commit -m "$(cat <<EOF
Setup job branch: $job_name

- Profile: $profile_name
- Branch: $branch_name
- Token generated for private resume URL
EOF
)"
    success_msg "  Changes committed"

    # Summary
    echo ""
    echo "=========================================="
    success_msg "Job branch setup complete!"
    echo "=========================================="
    echo ""
    echo "Branch:  $branch_name"
    echo "Profile: $profile_name"
    echo "Token:   $token"
    echo ""
    echo "Files created:"
    echo "  - resume_builder/active_profile.txt"
    echo "  - resume_builder/resume_token.txt"
    echo ""
    echo "Next steps:"
    echo "  1. Run the resume builder to generate your customized resume"
    echo "  2. Push the branch when ready: git push -u origin $branch_name"
    echo ""
}

# Run main function with all arguments
main "$@"
