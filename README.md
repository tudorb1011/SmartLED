## SmartLEDs

This project is designed for the Raspberry Pi Pico with MicroPython to enable Wi-Fi connectivity and control an RGB LED via a web interface. It uses an OLED display for status updates and allows for both Access Point (AP) mode and Station (STA) mode functionality.

## Features

- **Wi-Fi Connectivity**:
  - Automatically connects to a stored Wi-Fi network.
  - If no network is configured, starts an AP mode with a web server for configuration.
  
- **Web Server**:
  - In AP mode, hosts a configuration page to select and save Wi-Fi credentials.
  - In STA mode, hosts a web page to control the RGB LED colors.

- **RGB LED Control**:
  - Set custom RGB colors using an intuitive color picker on the web interface.

- **Reset Button**:
  - Clears stored Wi-Fi credentials and restarts the device.

- **OLED Display**:
  - Displays connection status, IP address, and other information.

## Components

- **Raspberry Pi Pico**: The main microcontroller.
- **RGB LED**: Controlled via PWM pins.
- **OLED Display**: I2C-connected, for displaying text information.
- **Reset Button**: Physical button to reset Wi-Fi credentials.

## Pin Configuration

| Component        | Pin Number |
|------------------|------------|
| OLED SCL         | GP1        |
| OLED SDA         | GP0        |
| RGB LED (Red)    | GP16       |
| RGB LED (Green)  | GP17       |
| RGB LED (Blue)   | GP18       |
| Reset Button     | GP15       |

## Getting Started

### Prerequisites

- **MicroPython Firmware**: Install MicroPython on your Raspberry Pi Pico.
- **Required Libraries**:
  - `ssd1306.py` for the OLED display.
  - Built-in MicroPython modules: `network`, `socket`, `time`, `ujson`, `machine`.

### File Structure
- **project-directory:**
  - `main.py`             - Main script for running the project
  - `wifi_config.json`    - JSON file for storing Wi-Fi credentials
  - `ssd1306.py`          - Driver library for the OLED display

### Setup

1. **Connect Components**:
   - Connect the RGB LED and OLED display to the respective pins on the Pico.
   - Attach a button to the reset pin (GP15).

2. **Copy Files**:
   - Copy `main.py` and `ssd1306.py` to the Pico.
   - Ensure a blank `wifi_config.json` file exists.

3. **Run the Script**:
   - Restart the Pico. It will automatically execute `main.py`.

## Usage

### AP Mode

1. Connect to the "PICOLed" Wi-Fi network (default password: `testpico`).
2. Open a web browser and navigate to `192.168.4.1`.
3. Select your Wi-Fi network, enter the password, and click "Connect".

### STA Mode

1. The Pico connects to the configured Wi-Fi network and displays the IP address on the OLED.
2. Open a web browser and navigate to the displayed IP address.
3. Use the RGB LED control page to set colors.

### Resetting Wi-Fi Credentials

- Press the reset button (connected to GP15) to clear Wi-Fi credentials and restart.

## Example Web Pages

### AP Mode Configuration Page

- Displays a list of available Wi-Fi networks.
- Allows the user to enter credentials for their preferred network.

### STA Mode RGB Control Page

- Provides a color picker to set the RGB LED color.
- Displays the currently selected color in real time.

## Troubleshooting

- **OLED Not Displaying**:
  - Ensure the correct I2C pins are used (GP0 for SDA, GP1 for SCL).
- **Wi-Fi Connection Issues**:
  - Check the Wi-Fi credentials in `wifi_config.json`.
  - Verify the Wi-Fi network is in range.
- **AP Mode Not Starting**:
  - Clear credentials by pressing the reset button.


## Author

- Raul-Anton JAC
- Tudor-Neculai BÂLBĂ



