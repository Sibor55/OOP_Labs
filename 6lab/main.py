import json
from abc import ABC, abstractmethod


# Базовый класс для команд
class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass

    @abstractmethod
    def redo(self):
        pass


# Команда для печати символа
class PrintCharCommand(Command):
    def __init__(self, keyboard, char):
        self.keyboard = keyboard
        self.char = char

    def execute(self):
        self.keyboard.text += self.char
        self.keyboard.output(self.keyboard.text)

    def undo(self):
        self.keyboard.text = self.keyboard.text[:-1]
        self.keyboard.output(self.keyboard.text)

    def redo(self):
        self.execute()


# Команда для увеличения громкости
class VolumeUpCommand(Command):
    def __init__(self, keyboard):
        self.keyboard = keyboard
        self.prev_volume = keyboard.volume

    def execute(self):
        self.prev_volume = self.keyboard.volume
        self.keyboard.volume = min(100, self.keyboard.volume + 20)
        self.keyboard.output(f"volume increased +{self.keyboard.volume}%")

    def undo(self):
        self.keyboard.volume = self.prev_volume
        self.keyboard.output(f"volume decreased +{self.keyboard.volume}%")

    def redo(self):
        self.execute()


# Команда для уменьшения громкости
class VolumeDownCommand(Command):
    def __init__(self, keyboard):
        self.keyboard = keyboard
        self.prev_volume = keyboard.volume

    def execute(self):
        self.prev_volume = self.keyboard.volume
        self.keyboard.volume = max(0, self.keyboard.volume - 20)
        self.keyboard.output(f"volume decreased +{self.keyboard.volume}%")

    def undo(self):
        self.keyboard.volume = self.prev_volume
        self.keyboard.output(f"volume increased +{self.keyboard.volume}%")

    def redo(self):
        self.execute()


# Команда для управления медиаплеером
class MediaPlayerCommand(Command):
    def __init__(self, keyboard):
        self.keyboard = keyboard
        self.prev_state = keyboard.media_player_on

    def execute(self):
        self.prev_state = self.keyboard.media_player_on
        self.keyboard.media_player_on = not self.keyboard.media_player_on
        action = "launched" if self.keyboard.media_player_on else "closed"
        self.keyboard.output(f"media player {action}")

    def undo(self):
        self.keyboard.media_player_on = self.prev_state
        action = "launched" if self.keyboard.media_player_on else "closed"
        self.keyboard.output(f"media player {action}")

    def redo(self):
        self.execute()


# Класс для сохранения/восстановления состояния (Memento)
class KeyboardStateSaver:
    @staticmethod
    def save_to_file(bindings, filename):
        serialized = {}
        for key, cmd in bindings.items():
            if isinstance(cmd, PrintCharCommand):
                serialized[key] = {"type": "PrintCharCommand", "char": cmd.char}
            elif isinstance(cmd, VolumeUpCommand):
                serialized[key] = {"type": "VolumeUpCommand"}
            elif isinstance(cmd, VolumeDownCommand):
                serialized[key] = {"type": "VolumeDownCommand"}
            elif isinstance(cmd, MediaPlayerCommand):
                serialized[key] = {"type": "MediaPlayerCommand"}

        with open(filename, "w") as f:
            json.dump(serialized, f)

    @staticmethod
    def load_from_file(keyboard, filename):
        try:
            with open(filename, "r") as f:
                data = json.load(f)

            bindings = {}
            for key, cmd_data in data.items():
                cmd_type = cmd_data["type"]
                if cmd_type == "PrintCharCommand":
                    bindings[key] = PrintCharCommand(keyboard, cmd_data["char"])
                elif cmd_type == "VolumeUpCommand":
                    bindings[key] = VolumeUpCommand(keyboard)
                elif cmd_type == "VolumeDownCommand":
                    bindings[key] = VolumeDownCommand(keyboard)
                elif cmd_type == "MediaPlayerCommand":
                    bindings[key] = MediaPlayerCommand(keyboard)

            return bindings
        except FileNotFoundError:
            return {}


# Основной класс клавиатуры
class Keyboard:
    def __init__(self):
        self.text = ""
        self.volume = 0
        self.media_player_on = False
        self.bindings = {}
        self.history = []
        self.redo_stack = []

        # Файл для записи истории
        self.log_file = open("keyboard_log.txt", "w", encoding="utf-8")

    def output(self, message):
        """Вывод в консоль и запись в файл"""
        print(message)
        print(message, file=self.log_file)

    def assign_command(self, key, command):
        """Назначение команды на клавишу"""
        self.bindings[key] = command

    def press_key(self, key):
        """Обработка нажатия клавиши"""
        if key in self.bindings:
            cmd = self.bindings[key]
            cmd.execute()
            self.history.append(cmd)
            self.redo_stack = []
        else:
            self.output(f"Unknown command: {key}")

    def undo(self):
        """Отмена последнего действия"""
        if self.history:
            cmd = self.history.pop()
            cmd.undo()
            self.redo_stack.append(cmd)

    def redo(self):
        """Повтор последнего отмененного действия"""
        if self.redo_stack:
            cmd = self.redo_stack.pop()
            cmd.redo()
            self.history.append(cmd)

    def save_bindings(self, filename="keyboard_bindings.json"):
        """Сохранение привязок клавиш"""
        KeyboardStateSaver.save_to_file(self.bindings, filename)
        self.output(f"Bindings saved to {filename}")

    def load_bindings(self, filename="keyboard_bindings.json"):
        """Загрузка привязок клавиш"""
        self.bindings = KeyboardStateSaver.load_from_file(self, filename)
        self.output(f"Bindings loaded from {filename}")

    def close(self):
        """Завершение работы с клавиатурой"""
        self.log_file.close()


# Демонстрация работы
if __name__ == "__main__":
    kb = Keyboard()

    # Инициализация команд
    kb.assign_command("a", PrintCharCommand(kb, "a"))
    kb.assign_command("b", PrintCharCommand(kb, "b"))
    kb.assign_command("c", PrintCharCommand(kb, "c"))
    kb.assign_command("d", PrintCharCommand(kb, "d"))
    kb.assign_command("ctrl++", VolumeUpCommand(kb))
    kb.assign_command("ctrl+-", VolumeDownCommand(kb))
    kb.assign_command("ctrl+p", MediaPlayerCommand(kb))

    # Сохраняем привязки
    kb.save_bindings()

    # Последовательность действий
    actions = [
        "a",
        "b",
        "c",  # Печать символов
        "undo",
        "undo",
        "redo",  # Управление историей
        "ctrl++",
        "ctrl+-",  # Управление громкостью
        "ctrl+p",  # Запуск плеера
        "d",  # Печать символа
        "undo",
        "undo",  # Отмена действий
    ]

    # Выполняем действия
    for action in actions:
        if action == "undo":
            kb.undo()
        elif action == "redo":
            kb.redo()
        else:
            kb.press_key(action)

    # Завершаем работу
    kb.close()
