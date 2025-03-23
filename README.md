# Rinkhals Web UI app

A web interface for Rinkhals and Kobra-specific features.

## Features

- Toggle Rinkhals apps
- Toggle ACE auto-refill function
- Control ACE filament drying function
- Change ACE filament information
- Check for firmware updates in LAN or Cloud mode[^1]
- And more!

[^1]: Update checking connects to Anycubic Cloud with the printer ID.

## Installation

- Download the `update.swu` file for the app from the releases page.
- Copy it to a FAT32 formatted USB drive in a directory named: **aGVscF9zb3Nf**
- Plug the USB drive in the Kobra and the app will be installed.
- You will hear two beeps, the second one will tell you that the app is installed. There is no need to reboot afterwards.

You might need to enable the app via the Rinkhals touch UI for it to start.

The web UI can be accessed at: `http://<printer-ip>:1414`

## Development

To package the application as an `update.swu` file, run the following command from the repository root:

```
docker run --rm -it -v .\build:/build -v .\rinkhals-webui:/rinkhals-webui ghcr.io/jbatonnet/rinkhals/build /build/build-swu.sh "/rinkhals-webui"
```
