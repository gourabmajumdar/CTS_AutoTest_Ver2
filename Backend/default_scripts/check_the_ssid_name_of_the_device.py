import subprocess

def get_ssid_name():
    try:
        output = subprocess.run(
            ["dmcli", "eRT", "getv", "Device.WiFi.SSID.1.SSID"],
            capture_output=True, text=True
        )

        return output.stdout.strip()

    except Exception as e:
        print(f"Error running dmcli: {e}")
        return None

def main():
    print("Checking the SSID Name of the Device...")

    ssid_info = get_ssid_name()
    if ssid_info:
        print("SSID Name Information:")
        print(ssid_info)
        print("Test Result: COMPLETED")
    else:
        print("Test Result: FAILED")

if __name__ == '__main__':
    main()
