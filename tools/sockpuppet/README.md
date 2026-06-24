# Simple SOCKS Vpn Wrapper

A basic config may look like
```
[vpn]
name = "VPN"
host = "username@hostname
port = 1080
```
On MacOS, the app then shows up in the menu bar.

There is no support for connections that require you to type an SSH passphrase. It just so happens to work on MacOS because Keychain exists, but otherwise, it's a good reason to migrate to SSH certificates. Because the `rumps` dependency _requires_ MacOS, that turns out to be a nonissue!
