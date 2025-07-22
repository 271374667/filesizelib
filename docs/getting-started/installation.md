# Installation

Get Bytesize up and running in your Python environment quickly and easily.

## 📋 Requirements

Before installing Bytesize, ensure you have:

- **Python 3.9 or higher**
- **pip** (usually comes with Python)

You can check your Python version with:

```bash
python --version
# or
python3 --version
```

## 🚀 Installation Methods

=== "pip (Recommended)"

    Install from PyPI using pip:
    
    ```bash
    pip install bytesize
    ```
    
    For Python 3 specifically:
    
    ```bash
    pip3 install bytesize
    ```

=== "uv (Fast)"

    If you're using [uv](https://github.com/astral-sh/uv) for faster Python package management:
    
    ```bash
    uv add bytesize
    ```

=== "poetry"

    For projects using [Poetry](https://python-poetry.org/):
    
    ```bash
    poetry add bytesize
    ```

=== "pipenv"

    For projects using [Pipenv](https://pipenv.pypa.io/):
    
    ```bash
    pipenv install bytesize
    ```

=== "conda"

    If using Conda (when available):
    
    ```bash
    conda install bytesize
    ```

## 🔧 Development Installation

If you want to contribute to Bytesize or use the latest development version:

### From Source

```bash
# Clone the repository
git clone https://github.com/your-username/bytesize.git
cd bytesize

# Install in development mode
pip install -e .
```

### With Development Dependencies

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Or with uv
uv sync --dev
```

## ✅ Verify Installation

After installation, verify that Bytesize is working correctly:

```python
# Test basic import
from bytesize import Storage, StorageUnit

# Create a simple storage object
storage = Storage(1, StorageUnit.GB)
print(f"✅ Bytesize installed successfully! Test storage: {storage}")

# Test conversion
mb_value = storage.convert_to_mb()
print(f"✅ Conversion working: {mb_value}")
```

Expected output:
```
✅ Bytesize installed successfully! Test storage: 1.0 GB
✅ Conversion working: 1000.0 MB
```

## 🐍 Virtual Environment (Recommended)

We recommend installing Bytesize in a virtual environment to avoid conflicts:

=== "venv"

    ```bash
    # Create virtual environment
    python -m venv myproject
    
    # Activate (Linux/macOS)
    source myproject/bin/activate
    
    # Activate (Windows)
    myproject\Scripts\activate
    
    # Install Bytesize
    pip install bytesize
    ```

=== "conda"

    ```bash
    # Create conda environment
    conda create -n myproject python=3.11
    
    # Activate environment
    conda activate myproject
    
    # Install Bytesize
    pip install bytesize
    ```

## 🚨 Troubleshooting

### Common Issues

!!! warning "Permission Issues"
    If you get permission errors on Linux/macOS, try:
    ```bash
    pip install --user bytesize
    ```

!!! warning "Python Version"
    If you get a "Python version not supported" error:
    ```bash
    # Check your Python version
    python --version
    
    # Upgrade Python if needed (using pyenv example)
    pyenv install 3.11.0
    pyenv global 3.11.0
    ```

!!! warning "Package Not Found"
    If pip can't find the package:
    ```bash
    # Update pip first
    pip install --upgrade pip
    
    # Try installing again
    pip install bytesize
    ```

### Environment Issues

If you're having environment-related issues:

1. **Check Python path**:
   ```bash
   which python
   which pip
   ```

2. **Verify virtual environment**:
   ```bash
   pip list | grep bytesize
   ```

3. **Clear pip cache**:
   ```bash
   pip cache purge
   ```

## 🔄 Upgrading

To upgrade to the latest version:

```bash
# Upgrade with pip
pip install --upgrade bytesize

# Check version
python -c "import bytesize; print(bytesize.__version__)"
```

## 🗑️ Uninstallation

To remove Bytesize:

```bash
pip uninstall bytesize
```

## 📦 Dependencies

Bytesize has **zero external dependencies** - it only uses Python's standard library:

- `pathlib` - For cross-platform path operations
- `platform` - For platform detection
- `enum` - For storage unit definitions
- `typing` - For type annotations

This means:
- ✅ Faster installation
- ✅ Smaller footprint  
- ✅ Fewer security concerns
- ✅ Better compatibility

## 🎯 Next Steps

Now that you have Bytesize installed:

<div class="grid cards" markdown>

-   [:material-rocket-launch: **Quick Start**](quick-start.md)
    
    Jump right into using Bytesize with examples

-   [:material-school: **Basic Concepts**](concepts.md)
    
    Learn about storage units and core concepts

-   [:material-lightbulb-on: **Examples**](../examples/index.md)
    
    See real-world usage examples

-   [:material-api: **API Reference**](../api/index.md)
    
    Explore the complete API documentation

</div>