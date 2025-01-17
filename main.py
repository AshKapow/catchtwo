import re
import asyncio
import json
import random
import string
from discord.ext import commands
from discord.ext import tasks

version = 'v2.7.4'

with open('data/config.json', 'r') as file:
    info = json.loads(file.read())
    user_token = info['user_token']
    spam_id = info['spam_id']
    catch_id = info['catch_id']

with open('data/pokemon', 'r', encoding='utf8') as file:
    pokemon_list = file.read()
with open('data/legendary', 'r') as file:
    legendary_list = file.read()
with open('data/mythical', 'r') as file:
    mythical_list = file.read()
with open('data/wanted', 'r') as file:
    wanted_list = file.read()

num_pokemon = 0
shiny = 0
legendary = 0
mythical = 0
target_level = 0
min_level_range = 40
max_level_range = 60

poketwo = 716390085896962058
bot = commands.Bot(command_prefix="->", self_bot=True)
intervals = [1.5, 1.6, 1.7, 1.8, 1.9]


def solve(message):
    hint = []
    for i in range(15, len(message) - 1):
        if message[i] != '\\':
            hint.append(message[i])
    hint_string = ''
    for i in hint:
        hint_string += i
    hint_replaced = hint_string.replace('_', '.')
    solution = re.findall('^'+hint_replaced+'$', pokemon_list, re.MULTILINE)
    return solution


@tasks.loop(seconds=random.choice(intervals))
async def spam():
    channel = bot.get_channel(int(spam_id))
    await channel.send("".join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=random.randint(12, 24))))


@spam.before_loop
async def before_spam():
    await bot.wait_until_ready()

spam.start()


@bot.event
async def on_ready():
    print(f'Logged into account: {bot.user.name}')


@bot.event
async def on_message(message):
    channel = bot.get_channel(int(catch_id))
    if message.channel.id == int(catch_id):
        if message.author.id == poketwo:
            if message.embeds:
                embed_title = message.embeds[0].title
                if 'wild pokémon has appeared!' in embed_title:
                    spam.cancel()
                    await asyncio.sleep(1)
                    await channel.send('p!h')
                elif "Congratulations" in embed_title:
                    embed_content = message.embeds[0].description
                    if 'now level' in embed_content:
                        global target_level
                        global min_level_range
                        global max_level_range
                        split = embed_content.split(' ')
                        a = embed_content.count(' ')
                        level = int(split[a].replace('!', ''))
                        if target_level == 0:
                            target_level = random.randint(
                                min_level_range, max_level_range)
                            print(f'Level {target_level} selected as target')
                        print(
                            f'Current level is {level}, target level is {target_level}')
                        if level >= target_level:
                            print(
                                f'Selected pokemon has reached level {level} switching to next pokemon')
                            with open('data/level', 'r') as file:
                                to_level = file.readline()
                            await channel.send(f'p!s {to_level}')
                            print(f'Selecting pokemon {to_level}')
                            target_level = random.randint(
                                min_level_range, max_level_range)
                            print(f'Level {target_level} selected as target')

                            with open('data/level', 'r') as fi:
                                data = fi.read().splitlines(True)
                            with open('data/level', 'w') as fo:
                                fo.writelines(data[1:])
            else:
                content = message.content
                if 'The pokémon is ' in content:
                    if not len(solve(content)):
                        print('Pokemon not found.')
                    else:
                        for i in solve(content):
                            await asyncio.sleep(1)
                            if re.findall('^'+i+'$', wanted_list, re.MULTILINE):
                                print(f'{i} is in the wanted list - CAPTURING')
                                await channel.send(f'p!c {i}')
                            else:
                                print(
                                    f'{i} is not in the wanted list')
                    check = random.randint(1, 240)
                    if check == 1:
                        await asyncio.sleep(900)
                        spam.start()
                    else:
                        await asyncio.sleep(1)
                        spam.start()

                elif 'Congratulations' in content:
                    global shiny
                    global legendary
                    global num_pokemon
                    global mythical
                    num_pokemon += 1
                    split = content.split(' ')
                    pokemon = split[7].replace('!', '')
                    if 'seem unusual...' in content:
                        shiny += 1
                        print(f'Shiny Pokémon caught! Pokémon: {pokemon}')
                        print(
                            f'Shiny: {shiny} | Legendary: {legendary} | Mythical: {mythical}')
                    elif re.findall('^'+pokemon+'$', legendary_list, re.MULTILINE):
                        legendary += 1
                        print(f'Legendary Pokémon caught! Pokémon: {pokemon}')
                        print(
                            f'Shiny: {shiny} | Legendary: {legendary} | Mythical: {mythical}')
                    elif re.findall('^'+pokemon+'$', mythical_list, re.MULTILINE):
                        mythical += 1
                        print(f'Mythical Pokémon caught! Pokémon: {pokemon}')
                        print(
                            f'Shiny: {shiny} | Legendary: {legendary} | Mythical: {mythical}')
                    else:
                        print(f'Total Pokémon Caught: {num_pokemon}')
                        await channel.send(f'p!evolve l')
                elif 'human' in content:
                    spam.cancel()
                    print(
                        'Captcha detected; autocatcher paused. Press enter to restart, after solving captcha manually.')
                    input()
                    await channel.send('p!h')
    if not message.author.bot:
        await bot.process_commands(message)

print(
    f'Pokétwo Autocatcher {version}\nA second gen free and open-source Pokétwo autocatcher by devraza and ashkapow\nEvent Log:')
bot.run(f"{user_token}")
