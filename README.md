<h1 align="center">
    Discord.py Captcha
</h1>

<center style="margin-bottom:1rem;">A powerful package for discord.py v2 that allows you to easily create CAPTCHAs for Discord Servers.</center>

<div align="center">

  ![license](https://img.shields.io/badge/license-Apache%202.0-blue?style=flat-square)

  [![discord](https://img.shields.io/discord/667479986214666272?logo=discord&logoColor=white&style=flat-square)](https://diamonddigital.dev/discord)
  [![buy me a coffee](https://img.shields.io/badge/-Buy%20Me%20a%20Coffee-ffdd00?logo=Buy%20Me%20A%20Coffee&logoColor=000000&style=flat-square)](https://www.buymeacoffee.com/willtda)

</div>

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

# What do the CAPTCHAs look like?
Below is an image of what answering a CAPTCHA will look like when using the default settings:

![Image of Captcha](https://github.com/diamonddigitaldev/Discord.py-Captcha/blob/master/src/images/example_captcha.png)

# Installation

```
pip install discord.py-captcha
```

This will automatically install the required dependencies: **discord.py v2** and **Pillow**.

# Quick Start

```py
import discord
from discord.ext import commands
from discord_captcha import Captcha, CaptchaOptions

intents = discord.Intents.default()
intents.message_content = True  # enable "Message Content Intent" in the dev portal!
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

captcha = Captcha(bot, CaptchaOptions(
    role_id=123456789,
    channel_id=987654321,
    attempts=3,
    timeout=30,
))

@bot.event
async def on_member_join(member):
    await captcha.present(member)

bot.run("YOUR_BOT_TOKEN")
```

# Configuration

All options are passed via `CaptchaOptions`. Every option has a default, so you only need to set the ones you want to change.

## Options Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `role_id` | `int \| None` | `None` | The ID of the role to give the user when they solve the CAPTCHA. If `None`, no role is added. |
| `channel_id` | `int \| None` | `None` | The ID of a text channel to use as a fallback if the user's DMs are closed. If `send_to_text_channel` is `True`, the CAPTCHA is always sent here instead of DMs. Required if `send_to_text_channel` is `True`. |
| `send_to_text_channel` | `bool` | `False` | When `True`, the CAPTCHA is always sent to the text channel specified by `channel_id`, bypassing DMs entirely. When `False`, the bot tries DMs first and only falls back to the text channel if DMs are locked. |
| `kick_on_failure` | `bool` | `True` | Whether to automatically kick the user from the server if they fail the CAPTCHA or run out of time. |
| `case_sensitive` | `bool` | `True` | Whether the user's answer must match the exact casing of the CAPTCHA text. When `False`, the CAPTCHA only generates lowercase characters and answers are compared case-insensitively. |
| `attempts` | `int` | `1` | How many tries the user gets to solve the CAPTCHA before it counts as a failure. Each attempt has its own timeout window. |
| `timeout` | `float` | `60.0` | How many seconds the user has to respond on each attempt before it times out. |
| `show_attempt_count` | `bool` | `True` | Whether to display the remaining number of attempts in the embed footer. When the user only has one attempt, it shows "You have one attempt to solve the CAPTCHA." instead of a counter. |
| `custom_prompt_embed` | `discord.Embed \| None` | `None` | A custom embed to use for the CAPTCHA prompt message. If not provided, a default embed is used. The CAPTCHA image is automatically attached regardless. If `show_attempt_count` is enabled, the footer will be overwritten with the attempt counter. |
| `custom_success_embed` | `discord.Embed \| None` | `None` | A custom embed to show when the user solves the CAPTCHA. If not provided, a default green "CAPTCHA Solved!" embed is used. |
| `custom_failure_embed` | `discord.Embed \| None` | `None` | A custom embed to show when the user fails the CAPTCHA (wrong answers or timeout). If not provided, a default red "You Failed to Complete the CAPTCHA!" embed is used. The correct answer is shown in the default embed. |

## Example Configurations

**Minimal** — just verify, no role, no kick:
```py
captcha = Captcha(bot, CaptchaOptions(
    kick_on_failure=False,
))
```

**Strict** — one attempt, case-sensitive, 15 second timeout:
```py
captcha = Captcha(bot, CaptchaOptions(
    role_id=123456789,
    attempts=1,
    timeout=15,
    case_sensitive=True,
))
```

**Lenient** — multiple attempts, case-insensitive, sent in a channel:
```py
captcha = Captcha(bot, CaptchaOptions(
    role_id=123456789,
    channel_id=987654321,
    send_to_text_channel=True,
    case_sensitive=False,
    attempts=5,
    timeout=120,
    kick_on_failure=False,
))
```

# Usage

## Presenting a CAPTCHA (Built-In Generation)

The simplest way to use this package. A CAPTCHA image is generated automatically and sent to the user.

```py
@bot.event
async def on_member_join(member):
    result = await captcha.present(member)
    # result is True if solved, False if failed/timed out
```

## Presenting a CAPTCHA (Custom Image)

If you want to provide your own CAPTCHA image, pass a `CaptchaImageData` object to `present`:

```py
from discord_captcha import CaptchaImageData

@bot.event
async def on_member_join(member):
    with open("my_captcha.png", "rb") as f:
        image_bytes = f.read()

    await captcha.present(member, CaptchaImageData(
        image=image_bytes,
        text="the_answer"
    ))
```

## Manually Creating a CAPTCHA

You can use the `create_captcha` function to generate a CAPTCHA image without presenting it. This gives you control over the character length and which characters to exclude.

The character pool is `A-Z`, `a-z`, and `0-9` by default. Pass a `blacklist` string to exclude specific characters.

```py
from discord_captcha import create_captcha

# 4 characters, no numbers
my_captcha = await create_captcha(4, blacklist="0123456789")
# => CaptchaImageData(image=b'...', text='aBCd')

# pass it to present
await captcha.present(member, my_captcha)
```

# Events

Events let you hook into the CAPTCHA lifecycle for logging, analytics, or custom behavior. Register them as decorator callbacks on the `Captcha` instance.

Every callback receives a `CaptchaEventData` object with the following attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `member` | `discord.Member` | The member who is being presented the CAPTCHA. |
| `captcha_text` | `str` | The correct answer to the CAPTCHA. |
| `captcha_options` | `CaptchaOptions` | The options the CAPTCHA was configured with. |
| `responses` | `list[str]` | All answers the user has submitted so far. Empty for `on_prompt`. |
| `attempts` | `int` | How many attempts have been taken so far. `0` for `on_prompt`. |

## Available Events

**`on_prompt`** — Called when the CAPTCHA is first sent to the user, before they've had a chance to respond.

**`on_answer`** — Called every time the user submits a response, whether it's correct or not. Useful for logging individual attempts.

**`on_success`** — Called when the user answers correctly. At this point the role has already been added (if configured).

**`on_failure`** — Called when the user exhausts all their attempts with wrong answers. At this point the user has already been kicked (if configured).

**`on_timeout`** — Called when the user doesn't respond within the timeout window. At this point the user has already been kicked (if configured).

## Example

```py
@captcha.on_prompt
async def on_prompt(data):
    print(f"CAPTCHA sent to {data.member} (answer: {data.captcha_text})")

@captcha.on_answer
async def on_answer(data):
    print(f"{data.member} answered: {data.responses[-1]} (attempt {data.attempts})")

@captcha.on_success
async def on_success(data):
    print(f"{data.member} solved it in {data.attempts} attempt(s)")

@captcha.on_failure
async def on_failure(data):
    print(f"{data.member} failed after {data.attempts} attempt(s). Answers: {data.responses}")

@captcha.on_timeout
async def on_timeout(data):
    print(f"{data.member} didn't respond in time")
```

## Contact Us

- Need Help? [Join Our Discord Server](https://discord.gg/P2g24jp)!

- Found a Bug? [Open an Issue](https://github.com/diamonddigitaldev/Discord.py-Captcha/issues), or Fork and [Submit a Pull Request](https://github.com/diamonddigitaldev/Discord.py-Captcha/pulls) on our [GitHub Repository](https://github.com/diamonddigitaldev/Discord.py-Captcha)!
<hr>
<center>
<a href="https://diamonddigital.dev/"><strong>Created and maintained by</strong>
<img align="center" style="width:25%;height:auto" src="https://diamonddigital.dev/img/png/ddd_logo_text_transparent.png" alt="Diamond Digital Development Logo"></a>
</center>
