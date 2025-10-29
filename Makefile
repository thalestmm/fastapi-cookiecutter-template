.PHONY: build run clean install help

# Build the interactive generator
build:
	@echo "Building FastAPI Generator..."
	@go build -o fastapi-generator main.go
	@echo "✓ Build complete! Run with: ./fastapi-generator"

# Build and run the generator
run: build
	@./fastapi-generator

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -f fastapi-generator
	@rm -rf .venv
	@echo "✓ Clean complete!"

# Install Go dependencies
install:
	@echo "Installing Go dependencies..."
	@go mod download
	@echo "✓ Dependencies installed!"

# Show help
help:
	@echo "FastAPI Template Generator - Available commands:"
	@echo ""
	@echo "  make build    - Build the interactive generator"
	@echo "  make run      - Build and run the generator"
	@echo "  make clean    - Remove build artifacts and virtual environment"
	@echo "  make install  - Install Go dependencies"
	@echo "  make help     - Show this help message"
	@echo ""
	@echo "Quick start:"
	@echo "  1. make install"
	@echo "  2. make run"

