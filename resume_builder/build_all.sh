#!/bin/bash
# ============================================================================
# Resume Builder - Build Script
# ============================================================================
# This script builds resume files from YAML data with profile-based filtering.
#
# Features:
#   - Generates Markdown, HTML, and JSON output formats
#   - Supports profile-based filtering (default, leadership, technical)
#   - Can build single profile or all profiles at once
#
# Usage:
#   ./build_all.sh                     # Build with default profile
#   ./build_all.sh --profile leadership  # Build with specific profile
#   ./build_all.sh --all-profiles      # Build all available profiles
#   ./build_all.sh --help              # Show help message
#   ./build_all.sh --list-profiles     # List available profiles
#
# Output Files:
#   - Markdown files: resume_builder/*.md
#   - HTML files: *.html (project root)
#   - JSON files: output/*.json
#   - PDF files: *.pdf (project root, requires pandoc and wkhtmltopdf)
#
# Dependencies:
#   - Python 3 with PyYAML
#   - pandoc (for PDF generation)
#   - wkhtmltopdf (for PDF generation)
#
# ============================================================================

set -e  # Exit on error

# Script directory (where the Python generators are located)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output (if terminal supports it)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Helper Functions
# ============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# ============================================================================
# Usage and Help
# ============================================================================

show_help() {
    cat << EOF
Resume Builder - Build Script

USAGE:
    ./build_all.sh [OPTIONS]

OPTIONS:
    -h, --help              Show this help message and exit
    -l, --list-profiles     List all available profiles and exit
    -p, --profile NAME      Build with specified profile (default: default)
    --all-profiles          Build all available profiles
    --skip-pdf              Skip PDF generation (useful if pandoc/wkhtmltopdf not installed)
    --skip-html             Skip HTML generation
    --skip-json             Skip JSON generation
    --verbose               Show detailed output

EXAMPLES:
    # Build with default profile (full resume)
    ./build_all.sh

    # Build with leadership-focused profile
    ./build_all.sh --profile leadership

    # Build with technical-focused profile
    ./build_all.sh -p technical

    # Build all profiles at once
    ./build_all.sh --all-profiles

    # Build without PDF (if tools not available)
    ./build_all.sh --skip-pdf

    # List available profiles
    ./build_all.sh --list-profiles

AVAILABLE PROFILES:
    default     - Full Resume: Complete resume with all experience
    leadership  - Leadership Focused: Emphasizes people management and team leadership
    technical   - Technical Focused: Emphasizes technical skills and development

OUTPUT FILES:
    Markdown:   resume_builder/resume.md, resume_builder/resume-{profile}.md
    HTML:       index.html, resume-{profile}.html
    JSON:       output/resume.json, output/resume-{profile}.json
    PDF:        resume.pdf (requires pandoc and wkhtmltopdf)

For more information, see the project documentation.
EOF
}

list_profiles() {
    print_header "Available Profiles"
    cd "$SCRIPT_DIR"
    python3 md_generator.py --list-profiles
}

# ============================================================================
# Build Functions
# ============================================================================

# Build markdown for a specific profile
build_markdown() {
    local profile="$1"
    local verbose="$2"

    if [[ "$verbose" == "true" ]]; then
        print_info "Generating Markdown for profile: $profile"
    fi

    cd "$SCRIPT_DIR"
    if python3 md_generator.py --profile "$profile"; then
        if [[ "$verbose" == "true" ]]; then
            print_success "Markdown generated for profile: $profile"
        fi
        return 0
    else
        print_error "Failed to generate Markdown for profile: $profile"
        return 1
    fi
}

# Build HTML for a specific profile
build_html() {
    local profile="$1"
    local verbose="$2"

    if [[ "$verbose" == "true" ]]; then
        print_info "Generating HTML for profile: $profile"
    fi

    cd "$SCRIPT_DIR"
    if python3 html_generator.py --profile "$profile"; then
        if [[ "$verbose" == "true" ]]; then
            print_success "HTML generated for profile: $profile"
        fi
        return 0
    else
        print_error "Failed to generate HTML for profile: $profile"
        return 1
    fi
}

# Build JSON for a specific profile
build_json() {
    local profile="$1"
    local verbose="$2"

    if [[ "$verbose" == "true" ]]; then
        print_info "Generating JSON for profile: $profile"
    fi

    cd "$SCRIPT_DIR"
    if python3 json_generator.py --profile "$profile"; then
        if [[ "$verbose" == "true" ]]; then
            print_success "JSON generated for profile: $profile"
        fi
        return 0
    else
        print_error "Failed to generate JSON for profile: $profile"
        return 1
    fi
}

# Build PDF from markdown (only for default profile or specified profile)
build_pdf() {
    local profile="$1"
    local verbose="$2"

    # Determine input/output file names based on profile
    local md_file
    local html_file
    local pdf_file

    if [[ "$profile" == "default" ]]; then
        md_file="resume.md"
        html_file="resume.html"
        pdf_file="resume.pdf"
    else
        md_file="resume-${profile}.md"
        html_file="resume-${profile}.html"
        pdf_file="resume-${profile}.pdf"
    fi

    if [[ "$verbose" == "true" ]]; then
        print_info "Generating PDF for profile: $profile"
    fi

    # Check if pandoc is available
    if ! command -v pandoc &> /dev/null; then
        print_warning "pandoc not found - skipping PDF generation"
        return 0
    fi

    # Check if wkhtmltopdf is available
    if ! command -v wkhtmltopdf &> /dev/null; then
        print_warning "wkhtmltopdf not found - skipping PDF generation"
        return 0
    fi

    cd "$SCRIPT_DIR"

    # Check if markdown file exists
    if [[ ! -f "$md_file" ]]; then
        print_warning "Markdown file not found: $md_file - skipping PDF generation"
        return 0
    fi

    # Convert markdown to HTML
    if pandoc "$md_file" -f markdown -t html -c resume-stylesheet.css -s -o "$html_file"; then
        if [[ "$verbose" == "true" ]]; then
            print_info "Created intermediate HTML: $html_file"
        fi
    else
        print_error "Failed to create HTML from Markdown"
        return 1
    fi

    # Convert HTML to PDF
    if wkhtmltopdf --enable-local-file-access "$html_file" "$PROJECT_ROOT/$pdf_file"; then
        if [[ "$verbose" == "true" ]]; then
            print_success "PDF generated: $PROJECT_ROOT/$pdf_file"
        fi
        return 0
    else
        print_error "Failed to generate PDF"
        return 1
    fi
}

# Build cover letter (only for default profile)
build_coverletter() {
    local verbose="$1"

    if [[ "$verbose" == "true" ]]; then
        print_info "Generating cover letter"
    fi

    cd "$SCRIPT_DIR"

    # Check if cover letter generator exists
    if [[ ! -f "cover-letter_generator.py" ]]; then
        print_warning "Cover letter generator not found - skipping"
        return 0
    fi

    if python3 cover-letter_generator.py; then
        if [[ "$verbose" == "true" ]]; then
            print_success "Cover letter generated"
        fi
    else
        print_warning "Cover letter generation failed (non-critical)"
    fi

    # Generate cover letter PDF if pandoc/wkhtmltopdf available
    if command -v pandoc &> /dev/null && command -v wkhtmltopdf &> /dev/null; then
        if [[ -f "coverletter.md" ]]; then
            pandoc coverletter.md -f markdown -t html -c resume-stylesheet.css -s -o coverletter.html 2>/dev/null || true
            wkhtmltopdf --enable-local-file-access coverletter.html "$PROJECT_ROOT/coverletter.pdf" 2>/dev/null || true
            if [[ "$verbose" == "true" ]]; then
                print_success "Cover letter PDF generated"
            fi
        fi
    fi

    return 0
}

# Build all outputs for a single profile
build_profile() {
    local profile="$1"
    local skip_pdf="$2"
    local skip_html="$3"
    local skip_json="$4"
    local verbose="$5"

    local success=true

    print_header "Building profile: $profile"

    # Build Markdown (always required)
    if ! build_markdown "$profile" "$verbose"; then
        success=false
    fi

    # Build HTML (unless skipped)
    if [[ "$skip_html" != "true" ]]; then
        if ! build_html "$profile" "$verbose"; then
            success=false
        fi
    fi

    # Build JSON (unless skipped)
    if [[ "$skip_json" != "true" ]]; then
        if ! build_json "$profile" "$verbose"; then
            success=false
        fi
    fi

    # Build PDF (unless skipped)
    if [[ "$skip_pdf" != "true" ]]; then
        if ! build_pdf "$profile" "$verbose"; then
            success=false
        fi
    fi

    # Build cover letter only for default profile
    if [[ "$profile" == "default" ]]; then
        build_coverletter "$verbose"
    fi

    if [[ "$success" == "true" ]]; then
        print_success "Profile '$profile' built successfully"
        return 0
    else
        print_error "Profile '$profile' had some failures"
        return 1
    fi
}

# Build all available profiles
build_all_profiles() {
    local skip_pdf="$1"
    local skip_html="$2"
    local skip_json="$3"
    local verbose="$4"

    local profiles=("default" "leadership" "technical")
    local success_count=0
    local total=${#profiles[@]}

    print_header "Building All Profiles"
    print_info "Profiles to build: ${profiles[*]}"

    for profile in "${profiles[@]}"; do
        if build_profile "$profile" "$skip_pdf" "$skip_html" "$skip_json" "$verbose"; then
            success_count=$((success_count + 1))
        fi
    done

    echo ""
    print_header "Build Summary"
    print_info "Built $success_count/$total profiles successfully"

    if [[ $success_count -eq $total ]]; then
        print_success "All profiles built successfully!"
        return 0
    else
        print_error "Some profiles failed to build"
        return 1
    fi
}

# ============================================================================
# Main Script
# ============================================================================

main() {
    # Default values
    local profile="default"
    local all_profiles=false
    local skip_pdf=false
    local skip_html=false
    local skip_json=false
    local verbose=false

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                show_help
                exit 0
                ;;
            -l|--list-profiles)
                list_profiles
                exit 0
                ;;
            -p|--profile)
                if [[ -z "$2" || "$2" == -* ]]; then
                    print_error "Missing profile name after $1"
                    echo "Usage: ./build_all.sh --profile <profile_name>"
                    echo "Run './build_all.sh --list-profiles' to see available profiles."
                    exit 1
                fi
                profile="$2"
                shift 2
                ;;
            --all-profiles)
                all_profiles=true
                shift
                ;;
            --skip-pdf)
                skip_pdf=true
                shift
                ;;
            --skip-html)
                skip_html=true
                shift
                ;;
            --skip-json)
                skip_json=true
                shift
                ;;
            --verbose)
                verbose=true
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Run './build_all.sh --help' for usage information."
                exit 1
                ;;
        esac
    done

    # Verify we're in the right directory
    if [[ ! -f "$SCRIPT_DIR/resume.yaml" ]]; then
        print_error "resume.yaml not found in $SCRIPT_DIR"
        print_error "Please run this script from the resume_builder directory."
        exit 1
    fi

    # Verify Python dependencies
    if ! python3 -c "import yaml" 2>/dev/null; then
        print_error "PyYAML is not installed."
        print_error "Install with: pip install pyyaml"
        exit 1
    fi

    # Execute build
    if [[ "$all_profiles" == "true" ]]; then
        build_all_profiles "$skip_pdf" "$skip_html" "$skip_json" "$verbose"
    else
        # Validate profile exists
        if [[ ! -f "$SCRIPT_DIR/profiles/${profile}.yaml" ]]; then
            print_error "Profile '$profile' not found."
            echo "Available profiles:"
            list_profiles
            exit 1
        fi

        build_profile "$profile" "$skip_pdf" "$skip_html" "$skip_json" "$verbose"
    fi
}

# Run main function
main "$@"
