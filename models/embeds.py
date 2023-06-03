from discord import Embed


class DefaultEmbed(Embed):
    """
    A subclass of Embed.

    Attributes:
        color (int): The color of the embed.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, color=0xDB56A6)