class CaptchaError(ValueError):
    __module__ = "discord_captcha"

    HELP_URL = "https://diamonddigital.dev/discord"

    def __init__(self, message: str) -> None:
        super().__init__(f"{message}\nNeed Help? Join our Discord Server at '{self.HELP_URL}'")
