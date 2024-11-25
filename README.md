# IMAP Folder Sync

A Python script for synchronizing IMAP folders between two email accounts.

## Features

- Synchronizes emails between two IMAP servers
- Supports SSL/TLS encryption
- Uses Message-IDs to avoid duplicates
- Detailed logging with configurable output
- Dry-run mode for safe testing
- Preserves email flags (read, important, etc.)

## Installation

1. Python 3.6 or higher required
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
python imapsync.py --host1 source.imap.com --user1 user1 --password1 pass1 \
                   --host2 target.imap.com --user2 user2 --password2 pass2 \
                   [--dry-run] [--debug] [--log-file path/to/logfile]
```

### Parameters

- `--host1`: Source IMAP server (e.g., imap.gmail.com)
- `--user1`: Username for source server
- `--password1`: Password for source server
- `--host2`: Target IMAP server
- `--user2`: Username for target server
- `--password2`: Password for target server
- `--dry-run`: Optional. Simulates synchronization without making changes
- `--debug`: Optional. Enables detailed logging
- `--log-file`: Optional. Path to log file. If not specified, logs only to console

## Logging

By default, the script logs to console. You can optionally specify a log file using the `--log-file` parameter. Debug-level logging can be enabled with the `--debug` flag.

## Tests

Run unit tests with:

```bash
python -m unittest test_imapsync.py -v
```

## Security Notes

- Use app-specific passwords for services like Gmail
- Don't store passwords in plain text
- Use dry-run mode before the first real synchronization

## License

MIT License
