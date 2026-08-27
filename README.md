<h1 align="center">
    🎓 Discord.py Captcha 🎓
</h1>

<center style="margin-bottom:1rem;">A powerful package for discord.py v2 that allows you to easily create CAPTCHAs for Discord servers.</center>

[![PyPI](https://img.shields.io/pypi/v/discord.py-captcha?style=flat-square)](https://pypi.org/project/discord.py-captcha/) [![Discord Server](https://img.shields.io/discord/667479986214666272?logo=discord&logoColor=white&style=flat-square)](https://diamonddigital.dev/discord)

<a href="https://www.buymeacoffee.com/willtda" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

Creating a CAPTCHA system on Discord can be quite challenging for some, but it doesn't have to be that way. Discord.py Captcha handles everything for you, from CAPTCHA generation and sending, to handling user responses and validity.

### <u>What is a **CAPTCHA**?</u>

Put simply, a **CAPTCHA** is a question you have to answer to prove you are not a robot.

**CAPTCHA** is an acronym for:

**C**ompletely

**A**utomated

**P**ublic

**T**uring Test (to tell)

**C**omputers (and humans)

**A**part

To learn more about what a CAPTCHA is, you can [watch this video](https://www.youtube.com/watch?v=o1zNIm8GVPY&ab_channel=TomScott) by Tom Scott.

# Install Package

To install this awesome module, type the command shown below into your Terminal.

`pip install discord.py-captcha`

# Example Code

## Initial Setup:

```py
import discord
from discord.ext import commands
from discord_captcha import Captcha, CaptchaOptions

intents = discord.Intents.default()
intents.message_content = True  #IMPORTANT: make sure you enable "Message Content Intent" in the dev portal!
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

captcha = Captcha(bot, CaptchaOptions(
    role_id=123456789, #optional. if provided, the role will be added on success
    channel_id=987654321, #optional
    send_to_text_channel=False, #optional, defaults to False
    kick_on_failure=True, #optional, defaults to True. whether you want the bot to kick the user if the captcha is failed
    case_sensitive=True, #optional, defaults to True. whether you want the captcha responses to be case-sensitive
    attempts=3, #optional, defaults to 1. number of attempts before captcha is considered to be failed
    timeout=30, #optional, defaults to 60. time the user has to solve the captcha on each attempt in seconds
    show_attempt_count=True, #optional, defaults to True. whether to show the number of attempts left in embed footer
    custom_prompt_embed=discord.Embed(), #customise the embed that will be sent to the user when the captcha is requested
    custom_success_embed=discord.Embed(), #customise the embed that will be sent to the user when the captcha is solved
    custom_failure_embed=discord.Embed(), #customise the embed that will be sent to the user when they fail to solve the captcha
))

bot.run("Discord Bot Token")
```

### <u>**`channel_id`** Option Explained</u>
The `channel_id` option is the ID of the Discord Text Channel to Send the CAPTCHA to if the user's Direct Messages are locked.

Use the option `send_to_text_channel`, and set it to `True` to always send the CAPTCHA to the Text Channel.

### <u>**`send_to_text_channel`** Option Explained</u>
The `send_to_text_channel` option determines whether you want the CAPTCHA to be sent to a specified Text Channel instead of Direct Messages, regardless of whether the user's DMs are locked.

Use the option `channel_id` to specify the Text Channel.

## Presenting a CAPTCHA to a Member (With Built-In CAPTCHA Creation):

Discord.py Captcha can automatically create a CAPTCHA for you, if you don't want to create one yourself.

```py
@bot.event
async def on_member_join(member):
    #in your bot application in the dev portal, make sure you have intents turned on!
    await captcha.present(member) #captcha is created by the package, and sent to the member
```

## Presenting a CAPTCHA to a Member (With Custom CAPTCHA Image Data):

Don't like how the automatically created CAPTCHA looks? Simply pass in your own `CaptchaImageData` to the `present` method! You can also use Discord.py Captcha's Built-In CAPTCHA Creation to create your own CAPTCHA, and pass that in instead. (More on this [below](#manually-creating-a-captcha))

```py
@bot.event
async def on_member_join(member):
    #in your bot application in the dev portal, make sure you have intents turned on!
    captcha_image_buffer = #custom image as bytes
    captcha_image_text = #answer to the captcha as string
    await captcha.present(member, CaptchaImageData(image=captcha_image_buffer, text=captcha_image_text))
```

**Note:** When displaying a CAPTCHA to the user, the CAPTCHA image will automatically be attached to the `custom_prompt_embed` for you.

In addition, if you have the `show_attempt_count` option enabled, any embed footer text on the `custom_prompt_embed` will be overwritten with the number of attempts left.

## Manually Creating a CAPTCHA

You can use the `create_captcha` function to easily create your own CAPTCHA using Discord.py Captcha's Built-In CAPTCHA Creation. It also comes with broader control over the length of the CAPTCHA, and the characters you would like to use by using a blacklist.

**Note:** Built-In CAPTCHA Creation uses `A-Z`, `a-z` and `0-9`.

```py
from discord_captcha import create_captcha

async def example():
    #creating a CAPTCHA with 4 characters, and EXCLUDING numbers
    my_captcha = await create_captcha(4, "0123456789")
    print(my_captcha)
    # => CaptchaImageData(image=b'...', text='aBCd')

    #create_captcha resolves to an object that can be passed into the present method
    await captcha.present(member, my_captcha)
```

# CAPTCHA Events

There are five events that you can use to log CAPTCHA actions, responses, and other details. They are:

- `on_prompt` - Emitted when a CAPTCHA is presented to a user.
- `on_answer` - Emitted when a user responds to a CAPTCHA.
- `on_success` - Emitted when a CAPTCHA is successfully solved.
- `on_failure` - Emitted when a CAPTCHA is failed to be solved.
- `on_timeout` - Emitted when a user does not solve the CAPTCHA in time.

All of these events are emitted by the `Captcha` class. Here's an example of how to use them:

```py
@captcha.on_success
async def on_success(data):
    print(f"A Member has Solved a CAPTCHA!")
    print(data)
```

# What do the CAPTCHAs look like?
Below is an image of what answering a CAPTCHA will look like when using the default settings:

![Image of Captcha](https://github.com/diamonddigitaldev/Discord.py-Captcha/blob/master/src/images/example_captcha.png)


## Acknowledgements

### AI Disclosure

This project uses AI tools to aid development. Read our [AI Transparency & Quality Commitment](https://diamonddigital.dev/ai-transparency) statement for more information.

## Contact Me

- 👋 Need Help? [Join Our Discord Server](https://diamonddigital.dev/discord)!

- 👾 Found a Bug? [Open an Issue](https://github.com/diamonddigitaldev/Discord.py-Captcha/issues), or Fork and [Submit a Pull Request](https://github.com/diamonddigitaldev/Discord.py-Captcha/pulls) on our [GitHub Repository](https://github.com/diamonddigitaldev/Discord.py-Captcha)!
<hr>
<center>
<a href="https://diamonddigital.dev/"><strong>Created and maintained by</strong>
<img align="center" style="width:25%;height:auto" src="https://diamonddigital.dev/img/png/ddd_logo_text_transparent.png" alt="Diamond Digital Development Logo"></a>
</center>
