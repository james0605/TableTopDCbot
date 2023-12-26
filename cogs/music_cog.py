from ast import alias
import discord
from discord.ext import commands
from youtubesearchpython import VideosSearch
from yt_dlp import YoutubeDL
import asyncio

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
        #all the music related stuff
        self.is_playing = False
        self.is_paused = False

        # 2d array containing [song, channel]
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio/best'}
        self.FFMPEG_OPTIONS = {'options': '-vn'}
        # self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options':'-vn'}
        self.vc = None
        self.ytdl = YoutubeDL(self.YDL_OPTIONS)

     #searching the item on youtube
    def search_yt(self, item):
        if item.startswith("https://"):
            title = self.ytdl.extract_info(item, download=False)["title"]
            return{'source':item, 'title':title}
        search = VideosSearch(item, limit=1)
        return{'source':search.result()["result"][0]["link"], 'title':search.result()["result"][0]["title"]}

    async def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            #get the first url
            m_url = self.music_queue[0][0]['source']

            #remove the first element as you are currently playing it
            self.music_queue.pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url, download=False))
            song = data['url']
            self.vc.play(discord.FFmpegPCMAudio(song, executable= "ffmpeg.exe", **self.FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop))
        else:
            self.is_playing = False

    # infinite loop checking 
    async def play_music(self, ctx: commands.Context):
        
        print("playing music")
        print(f"music queue number :{len(self.music_queue)}")
        if len(self.music_queue) > 0:
            self.is_playing = True
            print("number > 0")
            m_url = self.music_queue[0][0]['source']
            #try to connect to voice channel if you are not already connected
            if self.vc == None or not self.vc.is_connected():
                print("not connect to voice channel")
                self.vc = await self.music_queue[0][1].connect()
                print(f"self.vc {self.vc}")  # <discord.voice_client.VoiceClient object at 0x0000012E30C61220>
                #in case we fail to connect
                if self.vc == None:
                    print("```Could not connect to the voice channel```")
                    await ctx.send("```Could not connect to the voice channel```")
                    return
            elif self.vc != self.music_queue[0][1]:
                print(f"from {self.vc} move to {self.music_queue}")
                await self.vc.move_to(self.music_queue[0][1])
            
            else:
                print("already in the same voice channel")
            # remove the first element as you are currently playing it
            print("start playing music")
            self.music_queue.pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url, download=False))
            song = data['url']
            self.vc.play(discord.FFmpegPCMAudio(song, executable= "F:/ffmpeg/ffmpeg/bin/ffmpeg.exe", **self.FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop))

        else:
            self.is_playing = False

    @commands.command(aliases=['j'])
    async def join(self, ctx: commands.Context):
        #這裡的指令會讓機器人進入call他的人所在的語音頻道
        voiceChannel = ctx.author.voice.channel
        
        await ctx.send("join called")
        print(ctx.voice_client)
        if ctx.author.voice == None:
            print("user is not in voice channel")
            await ctx.send("You are not connected to any voice channel")
        elif ctx.voice_client == None:
            print("connect to user's voice channel")
            self.vc = await voiceChannel.connect()
        elif ctx.voice_client != None:
            print("move to user's voice channel")
            self.vc = await ctx.voice_client.move_to(voiceChannel)
        else:
            print("already in the voice channel")
            await ctx.send("Already connected to a voice channel")
        print(f"self.vc {self.vc}")

    # leave command
    @commands.command(description="stops and disconnects the bot from voice", aliases=['l'])
    async def leave(self, ctx: commands.Context):
        self.is_playing = False
        self.is_paused = False
        await ctx.voice_client.disconnect()



    @commands.command(name="play", aliases=["p","playing"], help="Plays a selected song from youtube")
    async def play(self, ctx, *args):
        query = " ".join(args)
        try:
            voice_channel = ctx.author.voice.channel
        except:
            await ctx.send("```You need to connect to a voice channel first!```")
            return
        if self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("```Could not download the song. Incorrect format try another keyword. This could be due to playlist or a livestream format.```")
            else:
                if self.is_playing:
                    await ctx.send(f"**#{len(self.music_queue)+2} -'{song['title']}'** added to the queue")  
                else:
                    await ctx.send(f"**'{song['title']}'** added to the queue")  
                self.music_queue.append([song, voice_channel])
                if self.is_playing == False:
                    await self.play_music(ctx)
    @commands.command(name="debug", aliases=["d"])
    async def debug(self, ctx):
        print(f"is_playing {self.is_playing}")
        print(f"is_paused {self.is_paused}")
        await ctx.send(f"is_playing {self.is_playing}\nis_paused {self.is_paused}")

    @commands.command(name="pause", help="Pauses the current song being played")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name = "resume", aliases=["r"], help="Resumes playing with the discord bot")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name="skip", aliases=["s"], help="Skips the current song being played")
    async def skip(self, ctx):
        print(f"skip")
        if self.vc != None and self.vc:
            self.vc.stop()
            #try to play next in the queue if it exists
            await self.play_music(ctx)


    @commands.command(name="queue", aliases=["q"], help="Displays the current songs in queue")
    async def queue(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            retval += f"#{i+1} -" + self.music_queue[i][0]['title'] + "\n"

        if retval != "":
            await ctx.send(f"```queue:\n{retval}```")
        else:
            await ctx.send("```No music in queue```")

    @commands.command(name="clear", aliases=["c", "bin"], help="Stops the music and clears the queue")
    async def clear(self, ctx):
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("```Music queue cleared```")

    @commands.command(name="remove", help="Removes last song added to queue")
    async def re(self, ctx):
        self.music_queue.pop()
        await ctx.send("```last song removed```")
        
        
# Cog 載入 Bot 中
async def setup(bot: commands.Bot):
    print("setup music_cog")
    await bot.add_cog(music_cog(bot))