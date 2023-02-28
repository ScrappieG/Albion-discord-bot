
from typing import Optional
import discord
from discord import app_commands
from api import get_death_event
import sqlite3
from sql_queries import add_member, is_member,remove_member, find_guild_balance, add_regear, remove_regear, calculate_balance,find_regears

TOKEN = 'INSERT TOKEN'


MY_GUILD = discord.Object(id=123)  # replace with your guild id


TAX_RATE = .1 #can be changed whenever needed to but hardcoded seems to be better for everyone


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        
        self.tree = app_commands.CommandTree(self)

    #synchronize apps to one guild instead of multiple 
    #By having one guild it makes the commands faster :) as we dont need to specify a guild in every command

    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.all()
# give the bot intents (basically permissions)
client = MyClient(intents=intents)



@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

@client.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.Member ):
    """response to verifying regear request"""
    print('smile')
    emoji = reaction.emoji
    message = reaction.message
    

    if emoji == "✅" and message.channel.id == 123: #replace with regear channel id

        title = message.embeds[0].title
        print(title)
        temp = title.split('\n')
        print(temp)

        request_id = temp[0]
        request_id = request_id.split(':')
        request_id = request_id[1]
        print(request_id)

        death_id = temp[1]
        death_id = death_id.split(':')
        death_id = death_id[1]
        print(death_id)

        print('yes')
        conn = sqlite3.connect('bot.db')
        remove_regear(death_id, conn=conn)
        conn = sqlite3.connect('bot.db')
        calculate_balance(member_id=request_id, conn=conn)
        await message.channel.send(f'regear has been fullfilled {death_id}',delete_after=60)
        await message.delete()
        
    elif emoji == "🚫" and message.channel.id == 123: #replace with regear channel id
        title = message.embeds[0].title
        temp = title.split('\n')

        death_id = temp[1]
        death_id = death_id.split(':')
        death_id = death_id[1]
        print(death_id)

        request_id = temp[0]
        request_id = request_id.split(':')
        request_id = request_id[1]

        print('no')
        conn = sqlite3.connect('bot.db')
        remove_regear(death_id, conn=conn)
        conn = sqlite3.connect('bot.db')
        calculate_balance(member_id=request_id, conn=conn)
        await message.channel.send(f'regear has been removed {death_id}',delete_after=120)
        #do stuff
    else:
        return


        


@client.event
async def on_member_join(member: discord.Member):
    conn = sqlite3.connect('bot.db')
    if member.id == None:
        print(f'error adding member {member}')
    else:
        add_member(str(member.id), conn)
        await member.send('Welcome to goobers!')

@client.event
async def on_member_remove(member: discord.Member):
    conn = sqlite3.connect('bot.db')
    if member.id == None:
        print(f'error removing member {member}')
    else:
        remove_member(str(member.id), conn)
        

@client.tree.command()
async def banana(interaction: discord.Interaction):
    """Says hello!"""
    await interaction.response.send_message(f'banana., {interaction.user.mention}')


@client.tree.command()
@app_commands.describe(
    first_value='The first value you want to add something to',
    second_value='The value you want to add to the first value',
)
async def add(interaction: discord.Interaction, first_value: int, second_value: int):
    """Adds two numbers together."""
    await interaction.response.send_message(f'{first_value} + {second_value} = {first_value + second_value}')



@client.tree.command()
@app_commands.rename(text_to_send='text')
@app_commands.describe(text_to_send='Text to send in the current channel')
async def send(interaction: discord.Interaction, text_to_send: str):
    """Sends the text into the current channel."""
    await interaction.response.send_message(text_to_send)


@client.tree.command()
@app_commands.describe(member='The member you want to get the joined date from; defaults to the user who uses the command')
async def joined(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Says when a member joined."""
    member = member or interaction.user

    await interaction.response.send_message(f'{member} joined {discord.utils.format_dt(member.joined_at)}')


@client.tree.command()
@app_commands.rename(first_value = 'lootsplit_total')
@app_commands.describe(first_value='Total Ammount Of The Loot Split')
async def lootsplit(interaction: discord.Interaction, first_value: int, member: Optional[discord.Member] = None):
    """Creates easy loot splits"""

    member = member or interaction.user
    if member.voice == None:
        await interaction.response.send_message(f'{interaction.user.display_name} is not in a channel')
        #Checks if the user who typed the command is in a voice call

    else:

        channel = client.get_channel(member.voice.channel.id) # checks what channel the user is in

        members = channel.members #finds members connected to the channel

        memids = []

        for member in members:
            memids.append(member.id)
            #adds all the members to a list

        players = len(memids) #gets the ammount of people in the list

        tax = round(first_value * TAX_RATE)
        loot_without_tax = first_value *(1-TAX_RATE)

        Loot_value = round((loot_without_tax) / players) #calculation of the loot split

        await interaction.response.send_message(f'Loot value per person: {Loot_value} Tax: {tax}')


@client.tree.command()
@app_commands.rename(
    first_value='player_name',
    second_value='death_id',
    )
@app_commands.describe(
    first_value='Player Name',
    second_value='Death ID',
    )
async def regear_request(interaction: discord.Interaction, first_value: str, second_value: str):

    member = interaction.user
    member_id = member.id


    print('regear started')

    if member_id == None:
        await interaction.response.send_message('error')
    regear_loadout = get_death_event(first_value,second_value)

    price = 0

    message_body = ''

    for i in range(len(regear_loadout)):
        quality = regear_loadout[i]['quality']
        if quality == 0:
            quality = 'normal'
        elif quality == 1:
            quality = 'good'
        elif quality == 2:
            quality = 'outstanding'
        elif quality == 3:
            quality = 'excellent'
        elif quality == 4:
            quality = 'masterpeice'

        price = regear_loadout[i]['price'] + price

        if regear_loadout[i]['slot'] == 'mount':
            message_body = message_body + f"\n{regear_loadout[i]['slot']}:\n {regear_loadout[i]['item']}\n price: {regear_loadout[i]['price']}\n"
        else:
            message_body = message_body + f"\n{regear_loadout[i]['slot']}:\n {regear_loadout[i]['tier']}.{regear_loadout[i]['enchant']} {quality} {regear_loadout[i]['en_name']}\n price: {regear_loadout[i]['price']}\n"


    price = round(price)
    conn = sqlite3.connect('bot.db')
    add_regear(discord_id=member_id,death_id=second_value, regear_ammount=price, conn=conn)
    conn = sqlite3.connect('bot.db')
    calculate_balance(member_id=member_id, conn=conn)
    conn=sqlite3.connect('bot.db')
    balance = find_guild_balance(member_id=member_id,conn=conn)
    await interaction.response.send_message(
        f'\nyour request for a regear has been sent Ammout: {price} Total Guild Balance:{balance}'
        
    )

    regear_channel = interaction.guild.get_channel(123)  # replace with your regear Channel

    embed = discord.Embed(title=f'Member_id:{member_id}\nDeath_id:{second_value}\nSet Cost: {price}')

    
            
    embed.description = (message_body + f'\nAmmount: {price} \nTotal: {balance}'
    )

    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
    embed.timestamp = interaction.created_at

    await regear_channel.send(embed=embed)



@client.tree.command()
async def register(interaction: discord.Interaction, member:Optional[discord.Member] = None):
    member = member or interaction.user
    conn = sqlite3.connect('bot.db')

    if member.id == None:
        await interaction.response.send_message(f'This does not appear to be a member',delete_after=60, ephemeral=True)
    else:
        members = []

        members = client.get_all_members()

        print(member.id)

        match = is_member(str(member.id), conn)

        print(match)

        if match == True:
            print('match == True')
            await interaction.response.send_message('This user has already been registered',delete_after=60, ephemeral=True)

        if member in members and match == False:
            add_member(str(member.id), conn)
            print(str(member.id))
            await interaction.response.send_message(f'{member.display_name} has been registered',delete_after=60, ephemeral=True)






@client.tree.context_menu(name='Show Join Date')
async def show_join_date(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(f'{member} joined at {discord.utils.format_dt(member.joined_at)}',delete_after=60, ephemeral=True)


@client.tree.context_menu(name='Report to Moderators')
async def report_message(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.send_message(
        f'Thanks for reporting this message by {message.author.mention} to our moderators.', ephemeral=True
    )

    # Handle report by sending it into a log channel
    log_channel = interaction.guild.get_channel(123) #replace with your log channel id

    embed = discord.Embed(title='Reported Message')
    if message.content:
        embed.description = message.content

    embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
    embed.timestamp = message.created_at

    url_view = discord.ui.View()
    url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))

    await log_channel.send(embed=embed, view=url_view)

@client.tree.context_menu(name='view guild balance')
async def view_guild_balance(interaction: discord.Interaction, member: discord.Member):

    conn = sqlite3.connect('bot.db')

    member_id = member.id

    balance = find_guild_balance(str(member_id), conn)
    print(balance)


    embed = discord.Embed(title='Guild Silver Balance')
            
    embed.description = (f'Total: {balance}')
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
    embed.timestamp = interaction.created_at

    await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=120)

@client.tree.context_menu(name='view regears')
async def view_regears(interaction: discord.Interaction, member: discord.Member):
    conn=sqlite3.connect('bot.db')
    regears = find_regears(member_id=member.id, conn=conn)
    print(regears)
    message = ''
    if regears == -1:
        embed = discord.Embed(title=f'{member.display_name} has no regears')
        await interaction.channel.send(embed=embed, delete_after=120)
    else:
        for i in range(len(regears)):
            message=(f"death id: {regears[i]['death_id']} price \nfor regear: {regears[i]['regear_ammount']}")+message
        
        embed = discord.Embed(title=f'Regear for {member.display_name}')
        embed.description=(message)
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=120)




    


client.run(TOKEN)