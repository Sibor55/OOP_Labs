# https://en.wikipedia.org/wiki/Logging_(computing)
import re
from abc import ABC, abstractmethod
from datetime import datetime


# 1. Протокол для фильтров
# Протокол/Интерфейс - определяет контракт
# (функционал по которому определяется реализация функции для классов(Должен быть match в фильтре, handle в обработчике)),
# который должны реализовать все классы фильтров
class ILogFilter(ABC):
    @abstractmethod
    def match(self, text: str) -> bool:
        pass


# 2. Реализации фильтров 
class SimpleLogFilter(ILogFilter):
    def __init__(self, pattern: str):
        self.pattern = pattern

    def match(self, text: str) -> bool:
        return self.pattern in text


class ReLogFilter(ILogFilter):
    def __init__(self, regex_pattern: str):
        self.pattern = re.compile(regex_pattern)

    def match(self, text: str) -> bool:
        return bool(self.pattern.search(text))


# 3. Протокол для обработчиков
class ILogHandler(ABC):
    @abstractmethod
    def handle(self, text: str):
        pass


# 4. Реализации обработчиков
class FileHandler(ILogHandler):
    def __init__(self, filename: str):
        self.filename = filename

    def handle(self, text: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.filename, "a") as f:
            f.write(f"[{timestamp}] {text}\n")


class ConsoleHandler(ILogHandler):
    def handle(self, text: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\033[94mCONSOLE [{timestamp}]: {text}\033[0m")  # Синий цвет


class SyslogHandler(ILogHandler):
    def __init__(self, app_name: str):
        self.app_name = app_name

    def handle(self, text: str):
        timestamp = datetime.now().strftime("%b %d %H:%M:%S")
        print(
            f"\033[92mSYSLOG [{timestamp}] {self.app_name}: {text}\033[0m"
        )  # Зеленый цвет

# Типо реализация сокетхендлера, на самом деле через сокет надо было и нужно поднимать сервер чтобы это делать
class SocketHandler(ILogHandler):
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def handle(self, text: str):
        print(
            f"\033[93mSOCKET [-> {self.host}:{self.port}]: {text}\033[0m"
        )  # Желтый цвет


# 5. Основной класс Logger(Композиция (агрегация) - logger содержит фильтры и обработчики как зависимости)
class Logger:
    def __init__(
        self, filters: list[ILogFilter] = None, handlers: list[ILogHandler] = None
    ):
        self.filters = filters or []
        self.handlers = handlers or []

    def log(self, text: str):
        # Проверка фильтров
        for log_filter in self.filters:
            if not log_filter.match(text):
                return  # Сообщение не проходит фильтрацию

        # Передача сообщения всем обработчикам
        for handler in self.handlers:
            handler.handle(text)


# 6. Демонстрация работы(Dependency Injection - зависимости создаются вне logger'а и передаются в него)
if __name__ == "__main__":

    # Создаем обработчики
    file_handler = FileHandler("3lab/app.log")
    console_handler = ConsoleHandler()
    syslog_handler = SyslogHandler("my_app")
    socket_handler = SocketHandler("127.0.0.1", 514)

    # Создаем фильтры
    error_filter = SimpleLogFilter("ERROR")
    db_filter = ReLogFilter(r"DB\w+")

    # Сценарий 1: Логирование ошибок в файл и консоль
    error_logger = Logger(
        filters=[error_filter], handlers=[file_handler, console_handler]
    )

    print("\nЛогирование ошибок:")
    error_logger.log("INFO: Application started")
    error_logger.log("ERROR: File not found")
    error_logger.log("WARNING: Low memory")
    error_logger.log("ERROR: Connection timeout")

    # Сценарий 2: Логирование событий БД в syslog и сокет
    db_logger = Logger(filters=[db_filter], handlers=[syslog_handler, socket_handler])

    print("\nЛогирование событий БД:")
    db_logger.log("DB_CONNECT: User admin connected")
    db_logger.log("API_CALL: GET /users")
    db_logger.log("DB_QUERY: SELECT * FROM users")
    db_logger.log("DB_DISCONNECT: Connection closed")

    # Сценарий 3: Комбинированные фильтры
    combined_logger = Logger(
        filters=[error_filter, db_filter], handlers=[console_handler, syslog_handler]
    )

    print("\nКомбинированная фильтрация (ERROR + DB):")
    combined_logger.log("DB_UPDATE: Users table updated")
    combined_logger.log("ERROR: DB_CONNECTION failed")
    combined_logger.log("INFO: Server restarted")

    print("\n" + "=" * 50)
    print("Проверьте файл 'app.log' для просмотра записанных логов")
    print("=" * 50)
