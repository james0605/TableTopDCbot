import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import re


Friday = ":grinning:"
Saturday = ":wink:"
busy = ":pleading_face:"
emoji_num = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
def checkOpt(message):
    print("checking Opt")
    res = None
    for i, emoji in enumerate(emoji_num):
        if message == emoji:
            res = i
            print(f"res = {i}")
            break
    if res == None:
        print("not found")
    return res
    

# 定義名為 Main 的 Cog
class Main(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.checkDateMessageID = None
        self.checkDate.start()
        
        
    # 前綴指令
    @commands.command(aliases=['gr'])
    async def getResult(self, ctx: commands.Context):
        print(f"check Result")
        message_id = self.checkDateMessageID
        try:
            # 透過 fetch_message 方法取得特定 ID 的訊息
            message = await ctx.channel.fetch_message(message_id)

            # 獲取訊息的所有反應
            reactions = message.reactions
            
            winDate = None
            winCount = 0
            
            # 逐一處理每個反應
            for reaction in reactions:
                print("in reaction for loop")
                if winCount < reaction.count:
                    print(reaction.emoji)
                    winDate = checkOpt(reaction.emoji) + 1
                    winCount = reaction.count
            
            result_text = f"最終決定: {winDate}"
            
            await ctx.send(result_text)

        except discord.NotFound:
            await ctx.send("Message not found.")
    
    @commands.command(aliases=['v'])
    async def vote(self, ctx: commands.Context, *, choice):
        cho = re.compile(r'\S+').findall(choice)
        if len(cho) > 2:
            embed = discord.Embed(title=cho[0], color = 0x0011ff)
            cho.pop(0)
            
            for i, ele in enumerate(cho):
                embed.add_field(name = f"{emoji_num[i]}{ele}", value = "\u200b", inline=False)
            msg = await ctx.send(embed=embed)
            
            for i, ele in enumerate(cho):
                await msg.add_reaction(emoji_num[i])
        else:
            embed = discord.Embed(title=cho[0], color=0x0011ff)
            embed.add_field(name=cho[1], value = "\u200b", inline=False)
            msg = await ctx.send(embed=embed)
            await msg.add_reaction("👍")
            await msg.add_reaction("👎")

    @tasks.loop(hours=24)
    async def checkDate(self):
        # check is Monday
        currentTime = datetime.now()
        if datetime.now().weekday() == 0:
            print("check Date")
            days_until_friday = (4 - currentTime.weekday() + 7) % 7
            nextFriday = currentTime + timedelta(days = days_until_friday)
            nextSaturday = nextFriday + timedelta(days=1)
            formattedFridayDate = nextFriday.strftime("%m/%d")
            formattedSaturdayDate = nextSaturday.strftime("%m/%d")
            
            
            channel_id = "your channel id"
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send("@everyone")
                embed = discord.Embed(title="桌遊夜", color = 0x0011ff)
                embed.add_field(name = f"{emoji_num[0]}{formattedFridayDate}", value = "\u200b", inline=False)
                embed.add_field(name = f"{emoji_num[1]}{formattedSaturdayDate}", value = "\u200b", inline=False)
                embed.add_field(name = f"{emoji_num[2]}Busy", value = "\u200b", inline=False)
                msg = await channel.send(embed=embed)
                self.checkDateMessageID = msg.id
                for i in range(3):
                    await msg.add_reaction(emoji_num[i])
            else:
                print("no channel")
    
    
    # 關鍵字觸發
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if message.content == "Hello":
            await message.channel.send("Hello, world!")

# Cog 載入 Bot 中
async def setup(bot: commands.Bot):
    await bot.add_cog(Main(bot))