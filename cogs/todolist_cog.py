import discord
from discord.ext import commands, tasks


def createDesctiption(todolist):
    description = ''
    for i, (name, is_done) in enumerate(todolist.items()):
        if is_done == True:
            description += f"{i}. ［ｖ］ **{name}**\n"    
        else: 
            description += f"{i}. ［　］ **{name}**\n"
    return description


class ToDoList_cog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.todolistID = None
        self.todolist = None
        self.title = None
        self.author = None
        
    @commands.command(aliases = ['td'], help = 'Create a ToDoList')
    async def todo(self, ctx:commands.Context, title):
        print("Create ToDoList")
        self.title = title
        self.author = ctx.author
        self.todolist = {}
        embed = discord.Embed(title=self.title, color = 0x0011ff, description='Type !add <task> to start adding tasks!')
        embed.set_author(name=self.author)
        self.todolistMsg = await ctx.send(embed=embed)
        print(f"self.todolistMsg {type(self.todolistMsg)}")
        
    
    @commands.command(aliases = ['a'], help='Add a task into ToDoList')
    async def add(self, ctx:commands.Context, task):
        await ctx.message.delete()
        if self.title == None:
            await ctx.send("You haven't Create a TodoList!")
            return
        print(f"Add task {task} into todolist {self.title}")
        self.todolist[task] = False
        des = createDesctiption(self.todolist)
        embed = discord.Embed(title=self.title, color = 0x0011ff, description=des)
        await self.todolistMsg.edit(embed=embed)

        
        
    @commands.command(aliases=['ch'], help='Check the Checkbox')
    async def check(self, ctx:commands.Context, task):
        # delete user's message
        await ctx.message.delete()
        # check the todolist checkbox
        print(f"check {task}") # str
        if task in self.todolist:
            self.todolist[task] = True
        else:
            await ctx.send(f"{task} not in todolist")
        # reprint the todolist message
        des = createDesctiption(self.todolist)
        newEmbed = discord.Embed(title=self.title, color = 0x0011ff, description=des)
        await self.todolistMsg.edit(embed=newEmbed)
        
    @commands.command(aliases=['uch'], help='Uncheck the Checkbox')
    async def uncheck(self, ctx:commands.Context, task):
        # delete user's message
        await ctx.message.delete()
        # uncheck the todolist checkbox
        print(f"uncheck {task}") # str
        if task in self.todolist:
            self.todolist[task] = False
        else:
            await ctx.send(f"{task} not in todolist")
        # reprint the todolist message
        des = createDesctiption(self.todolist)
        newEmbed = discord.Embed(title=self.title, color = 0x0011ff, description=des)
        await self.todolistMsg.edit(embed=newEmbed)
        
        
# Cog 載入 Bot 中
async def setup(bot: commands.Bot):
    print("setup todolist_cog")
    await bot.add_cog(ToDoList_cog(bot))