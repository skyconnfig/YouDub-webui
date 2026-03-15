# Testing

## Overview

**This project has no formal test suite.**

As stated in `AGENTS.md`: "This project has no formal test suite. To verify changes: 1. Manual testing 2. Integration testing via Gradio UI 3. Check imports"

## Current Testing Approach

### Manual Testing

1. **Run specific step function with test data**: Execute individual step modules with sample videos
   - Example: Run `step020_whisperx.py` on a test video folder

2. **Integration testing**: Run the full pipeline via Gradio UI
   - `python app.py` to start the web interface
   - Test with sample YouTube URLs

3. **Import verification**: Check that imports work correctly
   - `python -c "from youdub import *"`

## Testing Infrastructure

- **No test framework**: No pytest, unittest, or other testing framework
- **No test files**: No `test_*.py` or `*_test.py` files in the project
- **No test fixtures**: No mock data or fixtures

## Recommendations for Future Testing

1. **Add pytest framework**: Create `tests/` directory with pytest
2. **Unit tests**: Test individual functions in step modules
3. **Integration tests**: Test full pipeline with mock videos
4. **Mock external APIs**: Use responses library to mock OpenAI, Bilibili API calls
5. **CI/CD**: Add GitHub Actions workflow for automated testing