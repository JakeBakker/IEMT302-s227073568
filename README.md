## Beautiful Soup Local Extraction Example

This example demonstrates using Beautiful Soup in Python to extract structured data from locally-provided HTML content embedded directly in the script.

### Requirements

- Python 3.9+

### Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

### Run

```bash
python parse_local_events.py
```

The script prints a JSON array of events with fields like `title`, `date_iso`, `location`, and `description`.

# IEMT302-s227073568
