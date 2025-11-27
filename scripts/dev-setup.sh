#!/bin/bash
# Development environment setup script for markdown-vault
# This script automates the initial setup for new developers

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print colored message
print_msg() {
    echo -e "${GREEN}==>${NC} $1"
}

print_error() {
    echo -e "${RED}Error:${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}Warning:${NC} $1"
}

print_info() {
    echo -e "${BLUE}Info:${NC} $1"
}

# Check if Docker is installed
check_docker() {
    print_msg "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        print_info "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker."
        exit 1
    fi
    
    print_msg "✓ Docker is installed and running"
}

# Check if Docker Compose is available
check_docker_compose() {
    print_msg "Checking Docker Compose..."
    if ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not available."
        exit 1
    fi
    print_msg "✓ Docker Compose is available"
}

# Check if Make is installed
check_make() {
    print_msg "Checking Make installation..."
    if ! command -v make &> /dev/null; then
        print_warning "Make is not installed. You can still use docker compose commands directly."
        print_info "To install Make:"
        print_info "  - macOS: xcode-select --install"
        print_info "  - Ubuntu/Debian: sudo apt-get install build-essential"
        print_info "  - Fedora/RHEL: sudo dnf install make"
        return 1
    fi
    print_msg "✓ Make is installed"
    return 0
}

# Create necessary directories
create_directories() {
    print_msg "Creating necessary directories..."
    
    mkdir -p test_vault
    mkdir -p certs
    mkdir -p logs
    mkdir -p config
    
    print_msg "✓ Directories created"
}

# Create sample config if it doesn't exist
create_sample_config() {
    print_msg "Creating sample configuration..."
    
    if [ ! -f config/config.yaml ]; then
        cp config/config.example.yaml config/config.yaml
        print_msg "✓ Sample config created at config/config.yaml"
        print_info "Please edit config/config.yaml to customize your settings"
    else
        print_info "Config already exists at config/config.yaml"
    fi
}

# Initialize test vault
init_test_vault() {
    print_msg "Initializing test vault..."
    
    if [ ! -f test_vault/test.md ]; then
        cat > test_vault/test.md << 'EOF'
# Test Note

This is a test note for development.

## Features to Test

- [ ] File reading
- [ ] File writing
- [ ] File search
- [ ] File listing

## Sample Content

Lorem ipsum dolor sit amet, consectetur adipiscing elit.
EOF
        
        mkdir -p test_vault/folder1
        echo "# Note in Folder 1" > test_vault/folder1/note1.md
        
        mkdir -p test_vault/daily
        echo "# Daily Note - $(date +%Y-%m-%d)" > test_vault/daily/$(date +%Y-%m-%d).md
        
        print_msg "✓ Test vault initialized with sample files"
    else
        print_info "Test vault already contains files"
    fi
}

# Build Docker image
build_image() {
    print_msg "Building Docker development image..."
    print_warning "This may take a few minutes on first run..."
    
    docker compose -f docker-compose.dev.yml build
    
    print_msg "✓ Docker image built successfully"
}

# Start development environment
start_environment() {
    print_msg "Starting development environment..."
    
    docker compose -f docker-compose.dev.yml up -d
    
    print_msg "✓ Development environment started"
}

# Verify installation
verify_installation() {
    print_msg "Verifying installation..."
    
    # Wait a bit for container to be fully ready
    sleep 2
    
    # Check if container is running
    if docker compose -f docker-compose.dev.yml ps | grep -q "markdown-vault-dev"; then
        print_msg "✓ Container is running"
    else
        print_error "Container is not running"
        exit 1
    fi
    
    # Check if package is installed
    if docker compose -f docker-compose.dev.yml exec -T markdown-vault-dev python -c "import markdown_vault" 2>/dev/null; then
        print_msg "✓ Package is installed correctly"
    else
        print_error "Package installation failed"
        exit 1
    fi
}

# Print next steps
print_next_steps() {
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}║  ${NC}${BLUE}✓${NC} ${GREEN}Development Environment Setup Complete!${NC}           ${GREEN}║${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo ""
    
    if [ "$MAKE_AVAILABLE" = true ]; then
        echo "  1. Open shell in container:"
        echo -e "     ${YELLOW}make shell${NC}"
        echo ""
        echo "  2. Run the server:"
        echo -e "     ${YELLOW}make run-server${NC}"
        echo ""
        echo "  3. Run tests:"
        echo -e "     ${YELLOW}make test${NC}"
        echo ""
        echo "  4. View all available commands:"
        echo -e "     ${YELLOW}make help${NC}"
    else
        echo "  1. Open shell in container:"
        echo -e "     ${YELLOW}docker compose -f docker-compose.dev.yml exec markdown-vault-dev bash${NC}"
        echo ""
        echo "  2. Run the server:"
        echo -e "     ${YELLOW}docker compose -f docker-compose.dev.yml exec markdown-vault-dev python -m markdown_vault start --reload${NC}"
        echo ""
        echo "  3. Run tests:"
        echo -e "     ${YELLOW}docker compose -f docker-compose.dev.yml exec markdown-vault-dev pytest${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}Documentation:${NC}"
    echo "  - Makefile Guide: docs/MAKEFILE_GUIDE.md"
    echo "  - Configuration: docs/CONFIGURATION.md"
    echo "  - Development: README.dev.md"
    echo ""
    echo -e "${BLUE}Server will be available at:${NC}"
    echo "  https://127.0.0.1:27123"
    echo ""
}

# Main setup flow
main() {
    echo ""
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                                                           ║${NC}"
    echo -e "${BLUE}║        ${NC}markdown-vault Development Setup${BLUE}              ║${NC}"
    echo -e "${BLUE}║                                                           ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Check prerequisites
    check_docker
    check_docker_compose
    
    MAKE_AVAILABLE=false
    if check_make; then
        MAKE_AVAILABLE=true
    fi
    
    # Setup steps
    create_directories
    create_sample_config
    init_test_vault
    build_image
    start_environment
    verify_installation
    
    # Show next steps
    print_next_steps
}

# Run main function
main
