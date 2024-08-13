import discord
from discord.ext import tasks, commands
import requests
from datetime import datetime

# Initialize the bot with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Instagram user ID and Access Token (replace with your values)
INSTAGRAM_USER_ID = 'Your Instagram User ID'
INSTAGRAM_ACCESS_TOKEN = 'Your Instagram Access Token'

# Discord channel ID where the bot will send Instagram posts
DISCORD_CHANNEL_ID = 1255168131249213511

# Set to store the IDs of already shared posts
shared_post_ids = set()

# URL for Instagram logo
INSTAGRAM_LOGO_URL = "URL"

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    check_instagram_posts.start()

@tasks.loop(minutes=1)
async def check_instagram_posts():
    try:
        instagram_posts = get_latest_instagram_posts()

        if instagram_posts:
            for post in instagram_posts:
                if post['id'] not in shared_post_ids:
                    await send_instagram_post(post)
                    shared_post_ids.add(post['id'])
    except Exception as e:
        print(f'Error fetching Instagram posts: {e}')

async def send_instagram_post(post):
    channel = bot.get_channel(DISCORD_CHANNEL_ID)

    if channel is None:
        print(f'Error: Discord channel with ID {DISCORD_CHANNEL_ID} not found.')
        return

    # Check if 'caption' key exists in the post data
    if 'caption' in post:
        # Truncate the title if it exceeds 256 characters
        title = post['caption'][:256]
    else:
        title = 'Instagram Post'

    # Parse the timestamp to datetime
    post_time = datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00'))

    embed = discord.Embed(title=title, url=post.get('permalink', ''), color=0xFF0000, timestamp=post_time)
    embed.set_image(url=post.get('media_url', ''))
    embed.set_author(name="Instagram", icon_url=INSTAGRAM_LOGO_URL)
    
    await channel.send(embed=embed)

def get_latest_instagram_posts():
    try:
        response = requests.get(f'https://graph.instagram.com/{INSTAGRAM_USER_ID}/media?fields=id,caption,permalink,media_type,media_url,timestamp&access_token={INSTAGRAM_ACCESS_TOKEN}')
        response.raise_for_status()
        data = response.json()

        return data['data'] if 'data' in data else []
    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err.response.status_code} - {http_err}')
    except Exception as e:
        print(f'Error occurred: {e}')
    return []

# Run the bot with the token
bot.run('Your Bot Token ID')
