import time
from pynput import keyboard


def start_key_listener(actions={}, groups={}, rest = 0.1):
    def on_press(key):
        if key == keyboard.Key.esc:
            return False
        try:
            k = key.char
        except:
            k = key.name
        print(f"on_press({k})")
        try:
            if k in actions:
                actions[k](k)
            for g in groups:
                if k in g:
                    groups[g](k)
        except Exception as e:
            print(e)
        time.sleep(rest)

    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    listener.join()


if __name__ == "__main__":
    print('starting')
    start_key_listener()
