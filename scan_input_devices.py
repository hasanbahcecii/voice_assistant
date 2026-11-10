"""List local input devices; not imported by the browser app."""

import pyaudio


def scan_input_devices():
    audio = pyaudio.PyAudio()
    try:
        print("--- Audio input devices ---")
        for index in range(audio.get_device_count()):
            device = audio.get_device_info_by_index(index)
            if device.get("maxInputChannels", 0) > 0:
                print(
                    f"{index}: {device['name']} | channels={device['maxInputChannels']} | rate={int(device['defaultSampleRate'])} Hz"
                )
    finally:
        audio.terminate()


if __name__ == "__main__":
    scan_input_devices()
