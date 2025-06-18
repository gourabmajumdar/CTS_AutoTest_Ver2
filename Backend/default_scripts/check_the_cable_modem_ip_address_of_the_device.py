import subprocess
import re

def get_cm_ip():
    try:
        output = subprocess.run(
            ["dmcli", "eRT", "getv", "Device.DeviceInfo.X_COMCAST-COM_CM_IP"],
            capture_output=True, text=True
        )
        return output.stdout.strip()
    except Exception as e:
        print(f"Error running dmcli: {e}")
        return None

def extract_ip(dmcli_output):
    for line in dmcli_output.splitlines():
        if 'value:' in line:
            ip = line.split('value:')[-1].strip()
            if is_valid_ip(ip):
                return ip
    return None

def is_valid_ip(ip):
    # Simple regex for IPv4
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    # Simple regex for IPv6
    ipv6_pattern = r'^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$'
    return re.match(ipv4_pattern, ip) or re.match(ipv6_pattern, ip)

def main():
    print("Checking the Cable Modem IP Address of the Device...")

    raw_output = get_cm_ip()
    if raw_output:
        ip_address = extract_ip(raw_output)
        if ip_address:
            print(f"Cable Modem IP Address: {ip_address}")
            print("Test Result: COMPLETED")
        else:
            print("Output received, but no valid IP address found.")
            print("Raw Output:")
            print(raw_output)
            print("Test Result: FAILED")
    else:
        print("Test Result: FAILED")

if __name__ == '__main__':
    main()




