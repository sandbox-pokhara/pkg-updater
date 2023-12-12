# pkg-updater

A python script to update packages

```
$ pkg-updater my-pkg
Next update in 899s, press enter to continue...
Checking for updates...
Gracefully shutting down running processes...
Installing updates...
...
...
...
Restarting closed processes...
Complete.
```

## Installation

You can install the package via pip:

```bash
pip install pkg-updater
```

## Usage

```
usage: pkg-updater [-h] [--extra-index-url EXTRA_INDEX_URL] [--interval INTERVAL] [--delay-first DELAY_FIRST] [--restart RESTART] package_name

positional arguments:
  package_name

options:
  -h, --help            show this help message and exit
  --extra-index-url EXTRA_INDEX_URL
  --interval INTERVAL
  --delay-first DELAY_FIRST
  --restart RESTART
```

## License

This project is licensed under the terms of the MIT license.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Contact

If you want to contact me you can reach me at pradishbijukchhe@gmail.com.
