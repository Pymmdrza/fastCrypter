# Makefile for Encrypter Native Libraries
# Compiles C/C++ code to shared libraries (.so/.dll)

# Compiler settings
CC = gcc
CXX = g++
CFLAGS = -O3 -fPIC -Wall -Wextra -march=native -ffast-math
CXXFLAGS = -O3 -fPIC -Wall -Wextra -march=native -ffast-math -std=c++17
LDFLAGS = -shared

# Platform detection
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    PLATFORM = linux
    LIB_EXT = .so
    CFLAGS += -DLINUX
    CXXFLAGS += -DLINUX
    LDFLAGS += -lm
endif
ifeq ($(UNAME_S),Darwin)
    PLATFORM = macos
    LIB_EXT = .dylib
    CFLAGS += -DMACOS
    CXXFLAGS += -DMACOS
    LDFLAGS += -lm
endif
ifeq ($(OS),Windows_NT)
    PLATFORM = windows
    LIB_EXT = .dll
    CC = x86_64-w64-mingw32-gcc
    CXX = x86_64-w64-mingw32-g++
    CFLAGS += -DWINDOWS
    CXXFLAGS += -DWINDOWS
    LDFLAGS += -Wl,--out-implib,lib$@.a
endif

# Output directory
OUTDIR = ../libs/$(PLATFORM)

# Source files
CRYPTO_CORE_SRC = crypto_core.c
HASH_ALGORITHMS_SRC = hash_algorithms.cpp

# Output libraries
CRYPTO_CORE_LIB = $(OUTDIR)/libcrypto_core$(LIB_EXT)
HASH_ALGORITHMS_LIB = $(OUTDIR)/libhash_algorithms$(LIB_EXT)

# Default target
all: setup $(CRYPTO_CORE_LIB) $(HASH_ALGORITHMS_LIB)

# Create output directory
setup:
	@mkdir -p $(OUTDIR)
	@echo "Building for platform: $(PLATFORM)"
	@echo "Library extension: $(LIB_EXT)"

# Compile crypto_core library
$(CRYPTO_CORE_LIB): $(CRYPTO_CORE_SRC)
	@echo "Compiling crypto_core library..."
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $<
	@echo "✅ crypto_core library built: $@"

# Compile hash_algorithms library
$(HASH_ALGORITHMS_LIB): $(HASH_ALGORITHMS_SRC)
	@echo "Compiling hash_algorithms library..."
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -o $@ $<
	@echo "✅ hash_algorithms library built: $@"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf ../libs/
	@echo "✅ Clean completed"

# Install libraries to system (optional)
install: all
	@echo "Installing libraries to system..."
ifeq ($(PLATFORM),linux)
	sudo cp $(CRYPTO_CORE_LIB) /usr/local/lib/
	sudo cp $(HASH_ALGORITHMS_LIB) /usr/local/lib/
	sudo ldconfig
endif
ifeq ($(PLATFORM),macos)
	sudo cp $(CRYPTO_CORE_LIB) /usr/local/lib/
	sudo cp $(HASH_ALGORITHMS_LIB) /usr/local/lib/
endif
	@echo "✅ Libraries installed"

# Test libraries
test: all
	@echo "Testing libraries..."
	@echo "Checking if libraries can be loaded..."
ifeq ($(PLATFORM),linux)
	ldd $(CRYPTO_CORE_LIB)
	ldd $(HASH_ALGORITHMS_LIB)
endif
ifeq ($(PLATFORM),macos)
	otool -L $(CRYPTO_CORE_LIB)
	otool -L $(HASH_ALGORITHMS_LIB)
endif
	@echo "✅ Library test completed"

# Debug build
debug: CFLAGS += -g -DDEBUG -O0
debug: CXXFLAGS += -g -DDEBUG -O0
debug: all

# Release build with maximum optimization
release: CFLAGS += -DNDEBUG -flto -funroll-loops
release: CXXFLAGS += -DNDEBUG -flto -funroll-loops
release: LDFLAGS += -flto
release: all

# Cross-compile for Windows (from Linux)
windows:
	@echo "Cross-compiling for Windows..."
	$(MAKE) OS=Windows_NT

# Show build information
info:
	@echo "Build Information:"
	@echo "  Platform: $(PLATFORM)"
	@echo "  C Compiler: $(CC)"
	@echo "  C++ Compiler: $(CXX)"
	@echo "  C Flags: $(CFLAGS)"
	@echo "  C++ Flags: $(CXXFLAGS)"
	@echo "  LD Flags: $(LDFLAGS)"
	@echo "  Library Extension: $(LIB_EXT)"
	@echo "  Output Directory: $(OUTDIR)"

# Help
help:
	@echo "Encrypter Native Libraries Build System"
	@echo ""
	@echo "Targets:"
	@echo "  all      - Build all libraries (default)"
	@echo "  clean    - Clean build artifacts"
	@echo "  install  - Install libraries to system"
	@echo "  test     - Test built libraries"
	@echo "  debug    - Build with debug symbols"
	@echo "  release  - Build with maximum optimization"
	@echo "  windows  - Cross-compile for Windows"
	@echo "  info     - Show build information"
	@echo "  help     - Show this help"
	@echo ""
	@echo "Examples:"
	@echo "  make                 # Build all libraries"
	@echo "  make clean all       # Clean and rebuild"
	@echo "  make release         # Optimized build"
	@echo "  make debug test      # Debug build and test"

.PHONY: all setup clean install test debug release windows info help 