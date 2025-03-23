import network
import socket
import time
import ujson
from machine import Pin, reset, I2C, PWM
from ssd1306 import SSD1306_I2C

# OLED display settings
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
oled = SSD1306_I2C(128, 32, i2c)

# Wi-Fi credentials file
WIFI_CRED_FILE = "wifi_config.json"

#HELLO PICO
oled.fill(0)
oled.text('Hello, Pico', 15, 15)
oled.show()
time.sleep(2)

# AP settings
AP_SSID = "PICOLed"
AP_PASSWORD = "testpico"

# Pins for RGB LED
red_pin = PWM(Pin(16))
green_pin = PWM(Pin(17))
blue_pin = PWM(Pin(18))

red_pin.freq(1000)
green_pin.freq(1000)
blue_pin.freq(1000)

# Pins for reset button
reset_btn = Pin(15, Pin.IN, Pin.PULL_DOWN)

def clear_wifi_credentials():
    try:
        with open(WIFI_CRED_FILE, "w") as f:
            f.write("{}")
        print("Wi-Fi credentials cleared.")
        oled.fill(0)
        oled.text("Wi-Fi cleared!", 0, 0)
        oled.text("Restarting...", 0, 10)
        oled.show()
    except Exception as e:
        print("Error clearing Wi-Fi credentials:", e)
    reset()

def check_reset_button(pin):
    if pin.value() == 1:
        clear_wifi_credentials()

reset_btn.irq(trigger=Pin.IRQ_RISING, handler=check_reset_button)

def set_rgb_color(r, g, b):
    red_pin.duty_u16(int(r * 64))
    green_pin.duty_u16(int(g * 64))
    blue_pin.duty_u16(int(b * 64))

def start_ap_mode():
    wlan = network.WLAN(network.AP_IF)
    wlan.active(True)
    wlan.config(essid=AP_SSID, password=AP_PASSWORD)
    print("Access Point started:", AP_SSID)
    oled.fill(0)
    oled.text(f"SSID: {AP_SSID}", 0, 0)
    oled.text(f"PASS: {AP_PASSWORD}", 0, 10)
    oled.text("IP: 192.168.4.1", 0, 20)
    oled.show()
    return wlan

def scan_networks():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    networks = wlan.scan()
    return [(net[0].decode("utf-8"), net[3]) for net in networks]

def start_ap_web_server():
    wlan = start_ap_mode()
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(5)
    print("AP Web server running at 192.168.4.1")

    try:
        while True:
            cl, addr = s.accept()
            print("Client connected from", addr)
            try:
                request = cl.recv(1024).decode("utf-8")

                if "GET / " in request:
                    networks = scan_networks()
                    network_list = "".join(
                        f'<option value="{ssid}">{ssid} (Signal: {signal})</option>'
                        for ssid, signal in networks
                    )
                    response = f"""
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>Wi-Fi Setup</title>
</head>
<body>
    <h1>Wi-Fi Setup</h1>
    <form action="/connect" method="POST">
        <label for="ssid">Select Wi-Fi:</label>
        <select name="ssid" id="ssid" required>{network_list}</select>
        <label for="password">Password:</label>
        <input type="password" name="password" required>
        <button type="submit">Connect</button>
    </form>
</body>
</html>
"""
                    cl.send(response)

                elif "POST /connect" in request:
                    body = request.split("\r\n\r\n")[1]
                    params = {k: v for k, v in (x.split('=') for x in body.split('&'))}
                    ssid = params.get("ssid")
                    password = params.get("password")

                    if ssid and password:
                        with open(WIFI_CRED_FILE, "w") as f:
                            creds = {"ssid": ssid, "password": password}
                            f.write(ujson.dumps(creds))
                        cl.send("""  
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="5; url=http://192.168.4.1/redirecting.html" />
</head>
<body>
    <h1>Connecting to Wi-Fi...</h1>
</body>
</html>
""")
                        cl.close()
                        reset()
                    else:
                        cl.send("HTTP/1.1 400 Bad Request\n\nInvalid Wi-Fi credentials.")

                else:
                    cl.send("HTTP/1.1 404 Not Found\n\nPage not found.")

            except Exception as e:
                print("Error in AP web server:", e)
            finally:
                cl.close()

    except Exception as e:
        print("Critical error in AP web server:", e)
    finally:
        s.close()

# Start STA web server for LED control
def start_sta_web_server():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        return

    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse of the address
    s.bind(addr)
    s.listen(5)
    print("STA Web server running at", wlan.ifconfig()[0])

    try:
        while True:
            cl, addr = s.accept()
            print("Client connected from", addr)
            try:
                request = cl.recv(1024).decode("utf-8")

                if "GET / " in request:  # Display LED control page
                    response = f"""
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>RGB LED Control</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        label, input, button {{ margin: 5px 0; display: block; }}
        button {{ padding: 10px; background-color: #28a745; color: white; border: none; cursor: pointer; }}
        button:hover {{ background-color: #218838; }}
    </style>
    <script>
        function updateRGBFields(colorInput) {{
            const hex = colorInput.value.replace("#", "");
            const r = parseInt(hex.substring(0, 2), 16);
            const g = parseInt(hex.substring(2, 4), 16);
            const b = parseInt(hex.substring(4, 6), 16);
            
            document.getElementById("r").value = r;
            document.getElementById("g").value = g;
            document.getElementById("b").value = b;
        }}
    </script>
</head>
<body>
    <h1>RGB LED Control</h1>
    <form action="/set_rgb" method="POST">
        <label for="color">Pick a Color:</label>
        <input type="color" id="color" name="color" value="#000000" onchange="updateRGBFields(this)">
        
        <!-- Hidden fields for RGB values -->
        <input type="hidden" id="r" name="r" value="0">
        <input type="hidden" id="g" name="g" value="0">
        <input type="hidden" id="b" name="b" value="0">
        
        <button type="submit">Set Color</button>
    </form>
</body>
</html>
"""
                    cl.send(response)

                elif "POST /set_rgb" in request:  # Handle RGB color change
                    body = request.split("\r\n\r\n")[1]
                    params = parse_query(body)

                    # Debugging print statement to check received parameters
                    print("Received parameters:", params)

                    try:
                        r = int(params.get("r", 0))
                        g = int(params.get("g", 0))
                        b = int(params.get("b", 0))

                        # Validate ranges
                        if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
                            set_rgb_color(r, g, b)
                            response = f"""
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="1; url=http://{wlan.ifconfig()[0]}/" />
</head>
<body>
    <p>Color set to RGB({r}, {g}, {b})! Redirecting back...</p>
</body>
</html>
"""
                        else:
                            raise ValueError("RGB values out of range")
                    except Exception as e:
                        print("Error setting RGB color:", e)
                        response = f"""
HTTP/1.1 400 Bad Request
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>Error</title>
</head>
<body>
    <p>Invalid RGB values received.</p>
    <p>Please ensure values are between 0 and 255.</p>
</body>
</html>
"""
                    cl.send(response)

                else:
                    cl.send("HTTP/1.1 404 Not Found\n\nPage not found.")

            except Exception as e:
                print("Error in STA web server:", e)
            finally:
                cl.close()  # Ensure client connection is closed

    except Exception as e:
        print("Critical error in STA web server:", e)
    finally:
        s.close()  # Ensure the socket is closed

def parse_query(body):
    # Split the body into key-value pairs and decode them
    params = {}
    body_parts = body.split('&')
    for part in body_parts:
        key, value = part.split('=')
        params[key] = value
    return params

def main():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    try:
        with open(WIFI_CRED_FILE, "r") as f:
            creds = ujson.load(f)
            ssid = creds.get("ssid")
            password = creds.get("password")
    except Exception:
        ssid = password = None

    if ssid and password: 
        wlan.connect(ssid, password)
        for _ in range(20):
            if wlan.isconnected():
                break
            time.sleep(0.5)

        if wlan.isconnected():
            oled.fill(0)
            oled.text("Connected! IP:", 0, 0)
            oled.text(f"{wlan.ifconfig()[0]}", 0, 10)
            oled.show()
            start_sta_web_server()
        else:
            print("Failed to connect. Starting AP mode...")

    start_ap_web_server()

if __name__ == "__main__":
    main()

