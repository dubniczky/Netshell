# Netshell

A lightweight HTTP CLI Shell that enables custom command injection into vulnerable web applications with a familiar shell-like interface.

## Installation

Install using pip:

```sh
pip install netshell
```

or manually by downloading the git repository:

```sh
git clone https://github.com/dubniczky/Netshell
```

## Usage

The `q` query parameter of `http://example.com/vln.php` is vulnerable to command injections, then the following command connects to it and starts a shell-like environment:

```sh
httpshell -a http://example.com/vln.php -p q
```
```txt
Connection successful!

example.com > whoami
www-data
```

Use `httpshell --help` for all flags and options.

Command line options:
- `-h`, `--help` - show this help message and exit
- `--address`, `-a` _ADDRESS_ Target address containing the full path. E.g., http://example.com/vulnerable.php
- `--parameter`, `-p` _PARAMETER_ Parameter name where the injection will occur. E.g., 'cmd' for http://example.com/vulnerable.php?cmd=...
- -`-cookies`, `-c` _COOKIES_ Use cookies for the request
- -`-agent` _AGENT_ Set a custom User-Agent header for the requests
- `--prefix`, `-P` _PREFIX_ Set a custom prefix for the commands. This is usually the command escape. By default there is none. No modifications apply to this, so make sure to encode it properly if needed.
- `--suffix`, `-S` _SUFFIX_   Set a custom suffix for the commands. This is usually the command escape. By default there is none. No modifications apply to this, so make sure to encode it properly if needed.
- `--verbose`, `-v` Verbose output
- `--no-url-encode` Disable URL encoding of commands
- `--no-preflight` Skip preflight checks and go straight to the shell interface

## Testing

The `/test` folder contains a simple injectable web server that can be started using Docker Compose.

```sh
cd test
docker compose up
```

The injectable point is at `/good` path with the `p` query parameter. By contrast the `/bad` path is not injectable.

Then starting the shell
```sh
netshell -a http://localhost:8000/good -p q
```
