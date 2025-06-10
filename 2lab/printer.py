from enum import Enum
from typing import Self


ANSI_TEMPLATE = "\033[{}m\033[{}m{}"
CURSOR_MOVE = "\033[{};{}H{}"


class Color(Enum):
    TRANSPARENT = 0
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37


class Printer:
    _font_data: dict[str, list[str]] = {}
    _char_width: int = 0
    _char_height: int = 0

    def __init__(
        self,
        color: Color,
        position: tuple[int, int],
        symbol: str,
        background_color: Color = Color.TRANSPARENT,
    ) -> None:
        self.color = color
        self.bg_color = background_color
        self.symbol = symbol
        self.origin_x, self.origin_y = position
        self.current_x, self.current_y = self.origin_x, self.origin_y

    @classmethod
    def load_font(cls, filename: str = "font.txt") -> None:
        """
        Загружает шрифт из текстового файла, заданного вручную.
        Ожидается, что первые две строки содержат размеры, далее — блоки символов.
        """
        try:
            with open(filename, "r") as file:
                cls._font_data.clear()
                cls._char_width = int(file.readline().strip())
                cls._char_height = int(file.readline().strip())
                cls._font_data[" "] = [
                    " " * cls._char_width for _ in range(cls._char_height)
                ]

                while True:
                    name_line = file.readline()
                    if not name_line:
                        break

                    char = name_line.replace("-", "").strip()
                    if not char:
                        continue

                    lines = []
                    for _ in range(cls._char_height):
                        line = file.readline().rstrip()[: cls._char_width]
                        lines.append(line)

                    cls._font_data[char] = lines

        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки шрифта: {e}")

    @classmethod
    def print_(
        cls,
        text: str,
        color: Color,
        position: tuple[int, int],
        symbol: str,
        background_color: Color = Color.TRANSPARENT,
    ) -> None:
        """
        Статический метод вывода текста.
        """
        if not cls._font_data:
            cls.load_font()

        x, y = position
        for char in text:
            glyph = cls._font_data.get(char, cls._font_data[" "])
            for row, content in enumerate(glyph):
                rendered = content.replace("*", symbol)
                print(
                    CURSOR_MOVE.format(
                        y + row + 1,
                        x + 1,
                        ANSI_TEMPLATE.format(
                            color.value, background_color.value + 10, rendered
                        ),
                    ),
                    end="",
                )
            x += cls._char_width
        print()

    def __enter__(self) -> Self:
        print(
            ANSI_TEMPLATE.format(self.color.value, self.bg_color.value + 10, ""), end=""
        )
        return self

    def __exit__(self, *args) -> None:
        print(
            ANSI_TEMPLATE.format(
                Color.TRANSPARENT.value, Color.TRANSPARENT.value + 10, ""
            ),
            end="",
        )

    def print(self, text: str) -> None:
        """
        Печатает текст начиная с текущей позиции.
        """
        if not self._font_data:
            self.load_font()

        x = self.current_x
        y = self.current_y

        for char in text:
            glyph = self._font_data.get(char, self._font_data[" "])
            for row, content in enumerate(glyph):
                rendered = content.replace("*", self.symbol)
                print(CURSOR_MOVE.format(y + row + 1, x + 1, rendered), end="")
            x += self._char_width

        self.current_x = x
