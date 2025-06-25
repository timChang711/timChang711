# Sensor Logger

This project provides a simple Python script (`sensor_logger.py`) that
reads sensor data over a serial connection and logs it to a CSV file.

## Requirements

- Python 3
- `pyserial` library

## Usage

Connect your device that outputs data using the expected protocol to a
serial port (the script defaults to `COM29` but you can change this in
the code). Run the script from the command line:

```bash
python sensor_logger.py
```

The logger stores records in a CSV file named
`sensor_speedtest_<date>_<time>.csv`.

Interrupt with `Ctrl+C` to stop recording. The script prints the number
of samples received per second while running.
