import gpiod
from mpd import MPDClient
import time

play_pressed = 0
next_pressed = 0
volume_down_pressed = 0
volume_up_pressed = 0
client = MPDClient()

def reconnect():
    try:
        client.ping()
    except Exception:
        client.connect("127.0.0.1", 6600)
        client.update()

if __name__ == "__main__":
    client.idletimeout = None
    client.connect("127.0.0.1", 6600)

    chip = gpiod.Chip('gpiochip0')

    play = chip.get_line(25)
    next = chip.get_line(10)
    volume_down = chip.get_line(17)
    volume_up = chip.get_line(18)

    play.request(consumer='dahdo', type=gpiod.LINE_REQ_EV_BOTH_EDGES)
    next.request(consumer='dahdo', type=gpiod.LINE_REQ_EV_BOTH_EDGES)
    volume_down.request(consumer='dahdo', type=gpiod.LINE_REQ_EV_BOTH_EDGES)
    volume_up.request(consumer='dahdo', type=gpiod.LINE_REQ_EV_BOTH_EDGES)
    
    while True:
        reconnect()
        time.sleep(0.07)
        if play.get_value() == 0 and play_pressed == 0:
            play_pressed = 1
            print("play pressed")
            if not client.currentsong():
                client.play()
            else:
                client.pause()
        elif play.get_value() == 1 and play_pressed == 1:
            play_pressed = 0

        elif next.get_value() == 0 and next_pressed == 0:
            next_pressed = 1
            print("next pressed")
            client.next()
        elif next.get_value() == 1 and next_pressed == 1:
            next_pressed = 0
        
        if volume_down.get_value() == 0 and volume_down_pressed == 0:
            volume_down_pressed = 1
            print("volume down pressed")
            current_volume = int(client.status().get('volume'))
            new_volume = max(0, current_volume - 5)  # Decrease volume by 5 units
            client.setvol(new_volume)
        elif volume_down.get_value() == 1 and volume_down_pressed == 1:
            volume_down_pressed = 0

        if volume_up.get_value() == 0 and volume_up_pressed == 0:
            volume_up_pressed = 1
            print("volume up pressed")
            current_volume = int(client.status().get('volume'))
            new_volume = min(100, current_volume + 5)  # Increase volume by 5 units
            client.setvol(new_volume)
        elif volume_up.get_value() == 1 and volume_up_pressed == 1:
            volume_up_pressed = 0







  	
