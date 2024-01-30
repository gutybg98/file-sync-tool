# file-sync-tool
This is a Python script for synchronizing files and directories between two locations, with logging capabilities.

## Requirements

- Python 3.x

## Usage

1. Clone the repository:

    `git clone https://github.com/gutybg98/file-sync-tool`

2. Navigate to the directory:

    `cd file-sync-tool`

3. Run the script:

    `python sync_tool.py <src_path> <dst_path> <sync_interval> <log_path>`

- `src_path`: Path to the source folder.
- `dst_path`: Path to the destination folder.
- `sync_interval`: Synchronization interval in minutes.
- `log_path`: Path to the log file.

## Example
`python sync_tool.py /path/to/source /path/to/destination 5 /path/to/logfile.log`

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
