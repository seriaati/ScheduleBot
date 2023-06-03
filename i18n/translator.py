from pathlib import Path
from typing import Any, Dict

import yaml


class Translator:
    def __init__(self) -> None:
        self.lang_files: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """
        Load all language files in the 'i18n' folder.

        This method iterates over all YAML files in the 'i18n' folder and stores them in a dictionary.

        Returns:
            None
        """
        self.lang_files = {}
        for file in Path("i18n/langs").glob("*.yaml"):
            with open(file, "r", encoding="utf-8") as f:
                self.lang_files[file.stem] = yaml.safe_load(f)

    def translate(self, lang: str, context: str) -> str:
        """
        Translate a string to the specified language.

        Args:
            string (str): The string to translate.
            lang (str): The language to translate to.
            context (str): The context of the string.

        Returns:
            str: The translated string.
        """
        keys = context.split(".")
        try:
            value = self.lang_files[lang]
        except KeyError:
            value = self.lang_files["en-US"]
        for key in keys:
            value = value[key]
        return value

translator = Translator()