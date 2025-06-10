from printer import Printer, Color

if __name__ == "__main__":
    # Проталкиваем экран вверх
    print("\n" * 30)

    # Первый шрифт, красный, одиночный вызов
    Printer.load_font("2lab/font5.txt")
    Printer.print_("AB", Color.RED, (5, 2), "#", background_color=Color.TRANSPARENT)

    # Второй шрифт, зелёный, объектный стиль с контекстом
    Printer.load_font("2lab/font7.txt")
    with Printer(Color.GREEN, (0, 10), "@", background_color=Color.BLACK) as printer:
        printer.print("ABOBA")
        printer.print(" AB")
