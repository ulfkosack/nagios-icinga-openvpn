# nagios-icinga-openvpn

Nagios/Icinga check for OpenVPN availability monitoring

## What to do with the check
The checks must be run on the monitoring server

## How to use check_openvpn
The plugin is a normal check which must be run on the monitoring server. It queries the target OpenVPN server and outputs OK, etc.
```
$ ./check_openvpn -h
usage: check_openvpn [-h] [-p PORT] [-t] [-4 | -6] [--timeout TIMEOUT]
                     [--digest DIGEST] [--digest-size DIGEST_SIZE]
                     [--digest-key-client DIGEST_KEY_CLIENT]
                     [--digest-key-server DIGEST_KEY_SERVER]
                     [--tls-auth TLS_AUTH]
                     [--key-direction {0,1,bidirectional}]
                     [--tls-auth-inverse] [--tls-crypt TLS_CRYPT]
                     [--retrycount RETRYCOUNT] [--no-validation]
                     host

positional arguments:
  host                  the OpenVPN host name or IP

options:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  set port number (default is 1194)
  -t, --tcp             use tcp instead of udp
  -4, --ipv4            use IPv4 only
  -6, --ipv6            use IPv6 only
  --timeout TIMEOUT     set timeout in seconds, for udp counted per packet
                        (default is 2)
  --digest DIGEST       set digest algorithm (default is "sha1")
  --digest-size DIGEST_SIZE
                        set HMAC digest size
  --digest-key-client DIGEST_KEY_CLIENT
                        set client HMAC key
  --digest-key-server DIGEST_KEY_SERVER
                        set server HMAC key for packet validation
  --tls-auth TLS_AUTH   set tls-auth file
  --key-direction {0,1,bidirectional}
                        tls-auth key direction, use the "key-direction" value
                        of the client config; "bidirectional" if the config
                        has none (default is 1)
  --tls-auth-inverse    same as --key-direction 0 (kept for compatibility)
  --tls-crypt TLS_CRYPT
                        set tls-crypt file (requires the Python module
                        "cryptography")
  --retrycount RETRYCOUNT
                        number of udp retries before giving up (default is 3)
  --no-validation       do not validate response
```

## Using settings from a client config (.ovpn)
The check acts like an OpenVPN client, so take the values from a working
client config:

| Client config                          | check_openvpn option           |
|----------------------------------------|--------------------------------|
| `remote <host> <port>`                 | `host`, `-p <port>`            |
| `proto tcp` / `proto tcp-client`       | `-t`                           |
| `proto udp4` / `tcp4`                  | `-4`                           |
| `proto udp6` / `tcp6`                  | `-6`                           |
| `auth SHA512`                          | `--digest sha512`              |
| `tls-auth ta.key` or `<tls-auth>` block | `--tls-auth ta.key`           |
| `key-direction 1` or `tls-auth ta.key 1` | `--key-direction 1` (default) |
| `key-direction 0` or `tls-auth ta.key 0` | `--key-direction 0`           |
| no key direction given                 | `--key-direction bidirectional` |
| `tls-crypt tc.key` or `<tls-crypt>` block | `--tls-crypt tc.key`        |

An inline `<tls-auth>` or `<tls-crypt>` block has to be saved to a separate
file, including the `-----BEGIN/END OpenVPN Static key V1-----` lines.

Example for a client config with `remote vpn.example.com 1194 udp4`,
`auth SHA512`, a `<tls-auth>` block and `key-direction 1`:
```
$ ./check_openvpn -4 --digest sha512 --tls-auth ta.key vpn.example.com
OK: Response validated, checked HMAC
```

### tls-crypt
With `tls-crypt` the server silently drops every packet that is not
encrypted with the right key, so without `--tls-crypt` the check can only
report `CRIT: Not responding`. `--tls-crypt` encrypts the request like an
OpenVPN client and validates the encrypted answer. See
[issue #22](https://github.com/liquidat/nagios-icinga-openvpn/issues/22).

- `--tls-crypt` needs the Python module `cryptography`
  (Debian/Ubuntu: `python3-cryptography`, RHEL/Fedora: `python3-cryptography`).
  All other options work without it.
- There is no key direction for tls-crypt and `--digest` is not used
  (tls-crypt always uses HMAC-SHA256 and AES-256-CTR).
- `tls-crypt-v2` (per-client keys, "OpenVPN tls-crypt-v2 client key") is not
  supported yet. With it the check reports `CRIT: Not responding`.

Example for a client config with `remote vpn.example.com 1195 udp4` and a
`<tls-crypt>` block:
```
$ ./check_openvpn -4 -p 1195 --tls-crypt tc.key vpn.example.com
OK: Response validated, checked HMAC
```

### Key direction and --tls-auth-inverse
The help text of `--tls-auth-inverse` used to read "set tls-auth file
direction to inverse (1)", which suggested that it matches `key-direction 1`.
It actually matches `key-direction 0`; clients with `key-direction 1` work
without any option. See
[issue #23](https://github.com/liquidat/nagios-icinga-openvpn/issues/23).

`--key-direction` now takes the value straight from the client config and
also supports servers without a key direction (`bidirectional`).
`--tls-auth-inverse` still works as an alias for `--key-direction 0`.
