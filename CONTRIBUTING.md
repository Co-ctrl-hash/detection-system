# Contributing to Number Plate Detection Project

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect differing viewpoints and experiences

## How to Contribute

### Reporting Bugs

1. Check if the bug is already reported in [Issues](https://github.com/yourusername/plate-detection-yolov7/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, GPU)
   - Error messages and logs

### Suggesting Enhancements

1. Check existing feature requests
2. Create an issue with:
   - Clear use case
   - Proposed solution
   - Alternatives considered
   - Benefits and potential drawbacks

### Pull Requests

1. **Fork the repository**
2. **Create a branch**: `git checkout -b feature/your-feature-name`
3. **Make changes**:
   - Follow code style guidelines
   - Add tests for new functionality
   - Update documentation
4. **Commit**: Use clear, descriptive commit messages
5. **Push**: `git push origin feature/your-feature-name`
6. **Open PR**: Describe changes, link related issues

## Development Setup

```powershell
# Clone your fork
git clone https://github.com/yourusername/plate-detection-yolov7.git
cd plate-detection-yolov7

# Add upstream remote
git remote add upstream https://github.com/original/plate-detection-yolov7.git

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dev dependencies
pip install -r requirements.txt
pip install pytest black flake8 mypy

# Run tests
pytest tests/
```

## Code Style

### Python
- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting: `black src/`
- Use type hints where appropriate
- Maximum line length: 127 characters

### Documentation
- Docstrings for all public functions/classes
- Use Google style docstrings
- Update README.md for user-facing changes

### Example:

```python
def detect_plates(image: np.ndarray, conf_threshold: float = 0.25) -> List[Dict]:
    """Detect license plates in an image.
    
    Args:
        image: Input image as numpy array (BGR format).
        conf_threshold: Confidence threshold for detections (0-1).
    
    Returns:
        List of detection dictionaries with keys: bbox, confidence, class.
    
    Raises:
        ValueError: If image is empty or invalid.
    """
    pass
```

## Testing

- Write unit tests for new functions
- Run tests before submitting PR: `pytest tests/ -v`
- Aim for >80% code coverage
- Include edge cases and error conditions

## Commit Messages

Use conventional commits:

```
feat: add TensorRT export script
fix: correct bbox normalization in utils
docs: update installation guide for Windows
test: add unit tests for OCR module
refactor: simplify training config parsing
```

## Review Process

1. Automated checks must pass (CI/CD)
2. Code review by maintainer(s)
3. Address feedback
4. Merge when approved

## Areas for Contribution

### High Priority
- [ ] Improve OCR accuracy with custom CRNN
- [ ] Add REST API with FastAPI
- [ ] Implement tracking across frames
- [ ] Add web dashboard for monitoring
- [ ] Expand test coverage

### Medium Priority
- [ ] Support for more annotation formats
- [ ] Multi-language plate recognition
- [ ] Performance profiling tools
- [ ] Kubernetes deployment configs
- [ ] Benchmark suite for various GPUs

### Good First Issues
- [ ] Improve error messages
- [ ] Add more example scripts
- [ ] Fix typos in documentation
- [ ] Add logging to scripts
- [ ] Create tutorial videos

## Questions?

- Open a [Discussion](https://github.com/yourusername/plate-detection-yolov7/discussions)
- Email: hello@innovateintern.com

Thank you for contributing! 🎉
