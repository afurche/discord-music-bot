import wavelink
from discord.ext import commands
import asyncio
from discord import embeds, colour


class Bot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix='?')

    async def on_ready(self):
        print('Bot is ready!')


class Music(commands.Cog):
    """Music cog to hold Wavelink related commands and listeners."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.songs = asyncio.Queue()
        self.play_next_song = asyncio.Event()

        bot.loop.create_task(self.audio_player())

    async def audio_player(self):
        """Connect to our Lavalink nodes."""
        await self.bot.wait_until_ready()

        node = await wavelink.NodePool.create_node(bot=bot,
                                                   host="127.0.0.1",
                                                   port=2333,
                                                   password='1234')

        channel = self.bot.get_channel('insert channel id') # I couldn't find a solution to send "Playing: " message on text channel when !play was typed, so I hardcoded the channel

        while True:
            self.play_next_song.clear()
            song, guild = await self.songs.get()
            player = node.get_player(guild)
            embed = embeds.Embed(
                title='Music Player',
                color=colour.Colour.blurple()
            )
            embed.add_field(name='Playing:', value=f'{song.title}')
            await channel.send(embed=embed)
            await player.play(song)
            await self.play_next_song.wait()

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        print(f'Node: <{node.identifier}> is ready!')

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.YouTubeTrack, reason):
        print(f"Track {track.title} ended")
        self.play_next_song.set()

    @commands.Cog.listener()
    async def on_wavelink_track_exception(self, player: wavelink.Player, track: wavelink.YouTubeTrack, error):
        print(f"TrackException : track {track.title}")
        self.play_next_song.set()

    @commands.command()
    async def play(self, ctx: commands.Context, *, song: wavelink.YouTubeTrack):
        """
        Connect bot to voice channel if not connected

        Add song to queue
        """
        embed = embeds.Embed(
            title="Music Player",
            color=colour.Colour.blurple()
        )
        if not ctx.voice_client:
            embed.add_field(name=f'Hello *{ctx.author.display_name}*', value='Let\'s play some music !!!', inline=False)
            await ctx.author.voice.channel.connect(cls=wavelink.Player)

        player: wavelink.Player = ctx.voice_client
        if player.is_playing():
            embed.add_field(name='Added to queue:', value=f'{song.title}', inline=False)
            embed.add_field(name='*Songs in the queue:*', value=f'{self.songs.qsize() + 1}', inline=False)

        queue_item = (song, ctx.guild)
        await self.songs.put(queue_item)
        await ctx.send(embed=embed)

    @commands.command()
    async def pause(self, ctx: commands.Context):
        if not ctx.voice_client:
            await ctx.send("Player is not in the voice channel")
            return
        else:
            player: wavelink.Player = ctx.voice_client

        await player.pause()

    @commands.command()
    async def resume(self, ctx: commands.Context):
        if not ctx.voice_client:
            await ctx.send("Player is not in the voice channel")
            return
        else:
            player: wavelink.Player = ctx.voice_client

        await player.resume()

    async def empty_queue(self):
        for _ in range(self.songs.qsize()):
            await self.songs.get()

    @commands.command()
    async def dc(self, ctx: commands.Context):
        if not ctx.voice_client:
            await ctx.send("Player is not in the voice channel")
            return
        else:
            embed = embeds.Embed(
                title='Music Player',
                color=colour.Colour.blurple()
            )
            embed.add_field(name=f"Bye bye *{ctx.message.author.display_name}*", value='See ya later!')
            await ctx.send(embed=embed)
            player: wavelink.Player = ctx.voice_client
            await player.stop()
            await player.disconnect()


    @commands.command()
    async def vol(self, ctx: commands.Context, volume):
        if not ctx.voice_client:
            await ctx.send("Player is not in the voice channel")
            return
        else:
            player: wavelink.Player = ctx.voice_client
            await player.set_volume(int(volume))
            await ctx.send(f"Volume adjusted to {int(volume)}")

    @commands.command()
    async def skip(self, ctx: commands.Context):
        if not ctx.voice_client:
            await ctx.send("Player is not in the voice channel")
            return
        else:
            player: wavelink.Player = ctx.voice_client
            await player.stop()

    @commands.command()
    async def queue(self, ctx: commands.Context):

        embed = embeds.Embed(
            title="Player Queue",
            color=colour.Colour.blurple()
        )

        if self.songs.qsize() == 0:
            embed.add_field(name="*Oh no*", value="Queue is empty")
            await ctx.send(embed=embed)
            return

        for i in range(self.songs.qsize()):
            song, guild = await self.songs.get()
            embed.add_field(name=f"*Song {i+1}*", value=f'{song.title}', inline=False)
            queue_item = (song, ctx.guild)
            await self.songs.put(queue_item)
        await ctx.send(embed=embed)

    @commands.command()
    async def clear(self, ctx: commands.Context):
        await self.empty_queue()
        await ctx.send("Queue cleared")


bot = Bot()
bot.add_cog(Music(bot))
bot.run('Insert your bot token')
