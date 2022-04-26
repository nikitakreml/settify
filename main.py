from os import system
import program_variables
import sqlite3
import discord
import asyncio
from discord.ext import commands

#Connection to the DB
try:
    connection = sqlite3.connect('rating.db') 
    cursor = connection.cursor()
    print("DB successfully created and linked to the Sqlite")
    
except sqlite3.Error as error:
    print("SQLite connection Error", error)


cursor.execute("""CREATE TABLE IF NOT EXISTS user_rating(discord_id INTEGER UNIQUE PRIMARY KEY NOT NULL , rating INTEGER);""")
connection.commit()


#Creation bot instance
intents = discord.Intents.all()
client = commands.Bot(command_prefix='!',intents = intents)


#Command Handlers
@client.command()
@commands.has_permissions(manage_channels=True)
async def create_channel(ctx, ch_type, name):
     if(ch_type == 'text'):
         await ctx.guild.create_text_channel(name)
         await ctx.message.channel.send("The channel " + name + " successfully created!")
     elif(ch_type == 'voice'):
         await ctx.guild.create_voice_channel(name)
         await ctx.message.channel.send("The channel " + name + " successfully created!")
     else:
         await ctx.message.channel.send("Not correct channel type")

@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount:int):
   await ctx.channel.purge(limit=amount)

@client.command() #Ввод текста через ""
async def quiz(ctx, text):
   msg = await ctx.message.channel.send(text)
   await msg.add_reaction('✅')
   await msg.add_reaction('❌')

@client.command()
async def rate(ctx, mentioned_user: str, rating): 
    try:
        mentioned_user = mentioned_user.replace('!', '')
        mentioned_user = mentioned_user.replace('@', '')
        mentioned_user = mentioned_user.replace('<', '')
        mentioned_user = mentioned_user.replace('>', '')
        mentioned_user = mentioned_user.replace(' ', '')
        
        if(int(mentioned_user) != int(ctx.author.id)):
            try:
                user_rate = cursor.execute('SELECT rating FROM user_rating WHERE discord_id = (?)',(mentioned_user,)).fetchone()[0]
                if(rating == '+'): user_rate+=1
                elif(rating == '-'): user_rate-=1
                cursor.execute('UPDATE user_rating SET rating=(?) WHERE discord_id = (?)', (user_rate, mentioned_user))
            except:
                user_rate = 0
                if(rating == '+'): user_rate+=1
                elif(rating == '-'): user_rate-=1
                user_data = (mentioned_user, user_rate)
                cursor.execute("INSERT INTO user_rating VALUES(?,?)", user_data)

            connection.commit()
        else:
            await ctx.send("You're trying to rate yourself")
    except:
        await ctx.send('Something went wrong... Command Format is: rate @mentioned_user ["+" or "-"]') 

@client.command()
async def my_rating(ctx):
    myid = str(ctx.author.id)
    user_rate = cursor.execute('SELECT rating FROM user_rating WHERE discord_id = (?)',(myid,)).fetchone()[0]
    await ctx.send(user_rate)

@client.command()
async def event(ctx, message):
    await ctx.send(content = "@everyone "+ message)

@client.command() 
async def send_to_all(ctx, message):
    members = ctx.guild.members

    for member in members:
        try:
            await member.send(message)
            print('Successfull DM')
        except:
            print('Unsuccessfull DM')


#Bot start
client.run(program_variables.TOKEN)
