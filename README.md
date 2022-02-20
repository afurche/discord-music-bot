# discord-music-bot

Discord music bot written in Python using Discord.py and Wavelink. Should work on Python 3.8.

Lavalink server is required to run, configuration provided in application.yml file.

Provides following functionalities (commands):

!play - connects bot to the voice channel on which author of the command is in and adds songs to the queue (song starts to play if queue empty)

!pause - pauses the music

!resume - resumes the music

!stop - stops the music

!queue - shows the queue 

!clear - clears the queue

!vol - changes volume of a player (by providing values from 0 to 100 e.g. !vol 45)

!dc - disconnects bot from the channel
