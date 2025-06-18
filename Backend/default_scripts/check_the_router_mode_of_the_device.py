import subprocess

def get_router_mode():
    try:
        output = subprocess.run(
            ["dmcli", "eRT", "getv", "Device.X_CISCO_COM_DeviceControl.LanManagementEntry.1.LanMode"],
            capture_output=True, text=True
        )
        return output.stdout.strip()
    except Exception as e:
        print(f"Error running dmcli: {e}")
        return None

def extract_mode(dmcli_output):
    for line in dmcli_output.splitlines():
        if 'value:' in line:
            mode = line.split('value:')[-1].strip()
            if mode.lower() in ['router', 'bridge']:
                return mode
            elif mode == '':
                return 'null'
    return None

def main():
    print("Checking the Router Mode of the Device...")

    raw_output = get_router_mode()
    if raw_output:
        mode = extract_mode(raw_output)
        if mode in ['router', 'bridge']:
            print(f"Router Mode: {mode}")
            print("Test Result: COMPLETED")
        elif mode == 'null':
            print("Router Mode value is null or empty.")
            print("Test Result: FAILED")
        else:
            print("Output received, but router mode is unknown.")
            print("Raw Output:")
            print(raw_output)
            print("Test Result: FAILED")
    else:
        print("Test Result: FAILED")

if __name__ == '__main__':
    main()
