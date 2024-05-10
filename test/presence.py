from pypresence import Presence  # The simple rich presence client in pypresence
import time
from datetime import timedelta

client_id = "1238219157464416266"  # Put your Client ID in here
RPC = Presence(client_id)  # Initialize the Presence client
RPC.connect()  # Start the handshake loop
RPC.update(
    state="00:20:00 / 00:25:00 57% complete",
    details="Frieren: Beyond Journey's End - Das Ende der Reise",
    large_text="Frieren: Beyond Journey's End - Das Ende der Reise",
    large_image="https://aniworld.to/public/img/cover/frieren-beyond-journeys-end-stream-cover-SleDrDCyzexECWwDE0d0oQyX5sYIO008_220x330.jpg",
    # small_image as playing or stopped ?
    small_image="https://jooinn.com/images/lonely-tree-reflection-3.jpg",
    small_text="ff 15",
    #start=time.time(), # for paused
    #end=time.time() + timedelta(minutes=20).seconds   # for time left
) # Updates our presence
while True:  # The presence will stay on as long as the program is running
    time.sleep(15)  # Can only update rich presence every 15 seconds
