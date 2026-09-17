import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import phonenumbers
from phonenumbers import geocoder, carrier, timezone

# Render ko active rakhne ke liye Flask server
web_app = Flask('')

@web_app.route('/')
def home():
    return "Bot is alive and running!"

def run():
    web_app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.command()
async def lookup(ctx, *, phone_number: str):
    try:
        parsed_number = phonenumbers.parse(phone_number, None)
        if not phonenumbers.is_valid_number(parsed_number):
            await ctx.send("❌ Galat phone number! Country code ke sath dalein (e.g. +91XXXXXXXXXX)")
            return

        country = geocoder.description_for_number(parsed_number, "en")
        sim_carrier = carrier.name_for_number(parsed_number, "en")
        time_zones = timezone.time_zones_for_number(parsed_number)

        embed = discord.Embed(title="📱 Phone Number Info", color=0x00ff00)
        embed.add_field(name="Number", value=phone_number, inline=False)
        embed.add_field(name="Location/Country", value=country or "Unknown", inline=True)
        embed.add_field(name="Carrier/Network", value=sim_carrier or "Unknown", inline=True)
        embed.add_field(name="Timezone", value=", ".join(time_zones), inline=False)
        embed.set_footer(text="OSINT Lookup Bot")

        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
