import pyaudio

def scan_input_devices():
    p = pyaudio.PyAudio()
    print("\n--- Valid Audio Input Devices ---")
    
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        # Filter ONLY devices that have input channels (microphones)
        if dev.get('maxInputChannels') > 0:
            name = dev.get('name')
            channels = dev.get('maxInputChannels')
            rate = int(dev.get('defaultSampleRate'))
            print(f"Index: {i:2d} | Channels: {channels} | Rate: {rate}Hz | Name: {name}")
            
    p.terminate()

if __name__ == "__main__":
    scan_input_devices()