import json
import sys
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import urlopen


def get_json(url):
    """Read JSON from PyPI. Return None only for HTTP 404."""
    try:
        with urlopen(url, timeout=20) as response:
            return json.load(response)
    except HTTPError as error:
        if error.code == 404:
            return None
        raise


def main():
    # Optionally accept a different input filename.
    filename = sys.argv[1] if len(sys.argv) > 1 else "requirements.txt"
    lines = Path(filename).read_text(encoding="utf-8").splitlines()

    dependencies_checked = len(lines)
    packages_missing = 0
    versions_missing = 0
    oldest = None

    for line_number, line in enumerate(lines, start=1):
        line = line.strip()

        if not line:
            continue

        name, separator, version = line.partition("==")
        name = name.strip()
        version = version.strip()

        if not separator or not name or not version:
            raise ValueError(
                f"Line {line_number}: expected package==version"
            )

        package_url = (
            f"https://pypi.org/pypi/{quote(name, safe='')}/json"
        )

        # First check whether the package exists.
        package_data = get_json(package_url)

        if package_data is None:
            packages_missing += 1
            continue

        # Then check whether the requested version exists.
        version_url = (
            f"https://pypi.org/pypi/{quote(name, safe='')}/"
            f"{quote(version, safe='')}/json"
        )
        release_data = get_json(version_url)

        if release_data is None:
            versions_missing += 1
            continue

        files = release_data.get("urls", [])

        # A release without files has no first-file upload time.
        if not files:
            continue

        upload_time = files[0]["upload_time"]
        release_date = datetime.fromisoformat(upload_time)

        if oldest is None or release_date < oldest[0]:
            oldest = (release_date, name, version)

    print(f"Dependencies checked: {dependencies_checked}")
    print(f"Packages not on PyPI: {packages_missing}")
    print(f"Versions not on PyPI: {versions_missing}")

    if oldest is None:
        print("Oldest pinned release: None")
    else:
        release_date, name, version = oldest
        print(
            f"Oldest pinned release: "
            f"{name}=={version} ({release_date.year})"
        )


if __name__ == "__main__":
    main()