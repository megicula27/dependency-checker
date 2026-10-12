# PyPI Dependency Checker

Checks whether pinned Python packages and versions exist on PyPI.

## Requirements
Python 3.7+ and an internet connection.
No third-party libraries are required.

## Run
```bash
python check_dependencies.py
```

## Input
The requirements.txt file contains one package==version per line.

## Results
The script reports:
- Dependencies checked
- Packages not on PyPI
- Versions not on PyPI
- Oldest pinned release, using the first file's upload_time
