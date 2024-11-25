# IMAP Folder Sync

Simple Python script to synchronize IMAP folders between two email accounts. The script copies all emails from one IMAP server to another while preserving flags (read, important, etc.) and avoiding duplicates.

## Features

- Syncs emails between IMAP servers with SSL/TLS
- Prevents duplicates using Message-IDs
- Preserves email flags
- Dry-run mode for testing
- Detailed logging options

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run sync (use --dry-run first to test)
python imapsync.py --host1 source.imap.com --user1 user1 --password1 pass1 \
                   --host2 target.imap.com --user2 user2 --password2 pass2
```

## Options

- `--dry-run` Test run without making changes
- `--debug` Show detailed debug information
- `--log-file FILE` Save logs to file

## Security Tips

- Use app-specific passwords for Gmail etc.
- Test with --dry-run first
- Don't store passwords in scripts

## Tests

```bash
python -m unittest test_imapsync.py -v
```

## License

This is free and unencumbered software released into the public domain - do whatever you want with it.
