import json
from abc import ABC, abstractmethod


# Базовый класс для команд
class Command(ABC):
    @abstractmethod
    def execute(self, context):
        pass

    @abstractmethod
    def undo(self, context):
        pass

    @abstractmethod
    def redo(self, context):
        pass


# Команда для печати символа
class PrintCharCommand(Command):
    def __init__(self, char):
        self.char = char

    def execute(self, context):
        context['text'] += self.char
        return context['text']

    def undo(self, context):
        context['text'] = context['text'][:-1]
        return context['text']

    def redo(self, context):
        return self.execute(context)


# Команда для увеличения громкости
class VolumeUpCommand(Command):
    def __init__(self):
        self.prev_volume = None

    def execute(self, context):
        self.prev_volume = context['volume']
        context['volume'] = min(100, context['volume'] + 20)
        return f"volume increased +{context['volume']}%"

    def undo(self, context):
        current_volume = context['volume']
        context['volume'] = self.prev_volume
        return f"volume decreased +{context['volume']}%"

    def redo(self, context):
        return self.execute(context)


# Команда для уменьшения громкости
class VolumeDownCommand(Command):
    def __init__(self):
        self.prev_volume = None

    def execute(self, context):
        self.prev_volume = context['volume']
        context['volume'] = max(0, context['volume'] - 20)
        return f"volume decreased +{context['volume']}%"

    def undo(self, context):
        current_volume = context['volume']
        context['volume'] = self.prev_volume
        return f"volume increased +{context['volume']}%"

    def redo(self, context):
        return self.execute(context)


# Команда для управления медиаплеером
class MediaPlayerCommand(Command):
    def __init__(self):
        self.prev_state = None

    def execute(self, context):
        self.prev_state = context['media_player_on']
        context['media_player_on'] = not context['media_player_on']
        action = "launched" if context['media_player_on'] else "closed"
        return f"media player {action}"

    def undo(self, context):
        context['media_player_on'] = self.prev_state
        action = "launched" if context['media_player_on'] else "closed"
        return f"media player {action}"

    def redo(self, context):
        return self.execute(context)


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
    def load_from_file(filename):
        try:
            with open(filename, "r") as f:
                data = json.load(f)

            bindings = {}
            for key, cmd_data in data.items():
                cmd_type = cmd_data["type"]
                if cmd_type == "PrintCharCommand":
                    bindings[key] = PrintCharCommand(cmd_data["char"])
                elif cmd_type == "VolumeUpCommand":
                    bindings[key] = VolumeUpCommand()
                elif cmd_type == "VolumeDownCommand":
                    bindings[key] = VolumeDownCommand()
                elif cmd_type == "MediaPlayerCommand":
                    bindings[key] = MediaPlayerCommand()

            return bindings
        except FileNotFoundError:
            return {}


# Основной класс клавиатуры
class Keyboard:
    def __init__(self):
        self.context = {
            'text': "",
            'volume': 0,
            'media_player_on': False
        }
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
            result = cmd.execute(self.context)
            self.output(result)
            self.history.append((cmd, self.context.copy()))
            self.redo_stack = []
        else:
            self.output(f"Unknown command: {key}")

    def undo(self):
        """Отмена последнего действия"""
        if self.history:
            cmd, prev_context = self.history.pop()
            result = cmd.undo(prev_context)
            self.output(result)
            self.context = prev_context
            self.redo_stack.append((cmd, self.context.copy()))

    def redo(self):
        """Повтор последнего отмененного действия"""
        if self.redo_stack:
            cmd, next_context = self.redo_stack.pop()
            result = cmd.redo(next_context)
            self.output(result)
            self.context = next_context
            self.history.append((cmd, self.context.copy()))

    def save_bindings(self, filename="keyboard_bindings.json"):
        """Сохранение привязок клавиш"""
        KeyboardStateSaver.save_to_file(self.bindings, filename)
        self.output(f"Bindings saved to {filename}")

    def load_bindings(self, filename="keyboard_bindings.json"):
        """Загрузка привязок клавиш"""
        self.bindings = KeyboardStateSaver.load_from_file(filename)
        self.output(f"Bindings loaded from {filename}")

    def close(self):
        """Завершение работы с клавиатурой"""
        self.log_file.close()


# Демонстрация работы
if __name__ == "__main__":
    kb = Keyboard()

    # Инициализация команд
    kb.assign_command("a", PrintCharCommand("a"))
    kb.assign_command("b", PrintCharCommand("b"))
    kb.assign_command("c", PrintCharCommand("c"))
    kb.assign_command("d", PrintCharCommand("d"))
    kb.assign_command("ctrl++", VolumeUpCommand())
    kb.assign_command("ctrl+-", VolumeDownCommand())
    kb.assign_command("ctrl+p", MediaPlayerCommand())

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