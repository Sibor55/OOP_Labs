from enum import Enum
import inspect
from typing import Dict, Any, Optional, Type


class LifeStyle(Enum):
    PER_REQUEST = 1
    SCOPED = 2
    SINGLETON = 3


class Injector:
    def __init__(self):
        self.registry = {}
        self.singletons = {}
        self.scoped_instances = {}
        self.scope_stack = []

    def register(
        self,
        interface_type: Type,
        implementation: Any,
        lifestyle: LifeStyle = LifeStyle.PER_REQUEST,
        params: Optional[Dict] = None,
    ):
        self.registry[interface_type] = {
            "implementation": implementation,
            "lifestyle": lifestyle,
            "params": params or {},
        }

    def enter_scope(self):
        self.scope_stack.append({})

    def exit_scope(self):
        if self.scope_stack:
            self.scope_stack.pop()

    def get_instance(self, interface_type: Type) -> Any:
        if interface_type not in self.registry:
            raise ValueError(f"No registration found for {interface_type}")

        registration = self.registry[interface_type]
        impl = registration["implementation"]
        lifestyle = registration["lifestyle"]
        params = registration["params"]

        if lifestyle == LifeStyle.SINGLETON:
            if interface_type not in self.singletons:
                self.singletons[interface_type] = self._create_instance(impl, params)
            return self.singletons[interface_type]

        if lifestyle == LifeStyle.SCOPED:
            if self.scope_stack:
                current_scope = self.scope_stack[-1]
                if interface_type not in current_scope:
                    current_scope[interface_type] = self._create_instance(impl, params)
                return current_scope[interface_type]
            raise RuntimeError("Attempt to resolve Scoped dependency outside of scope")

        return self._create_instance(impl, params)

    def _create_instance(self, impl: Any, params: Dict) -> Any:
        # Фабричный метод
        if callable(impl) and not inspect.isclass(impl):
            return impl()

        # Игнорируем конструктор object
        if impl is object:
            return object.__new__(impl)

        # Анализ конструктора
        signature = inspect.signature(impl.__init__)
        dependencies = {}

        for name, param in signature.parameters.items():
            if name == "self":
                continue

            # Пропускаем *args и **kwargs
            if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                continue

            # Используем переданные параметры
            if name in params:
                dependencies[name] = params[name]
                continue

            # Разрешаем зависимости по типу
            if param.annotation != inspect.Parameter.empty:
                try:
                    dependencies[name] = self.get_instance(param.annotation)
                    continue
                except ValueError:
                    pass

            # Используем значение по умолчанию
            if param.default != inspect.Parameter.empty:
                dependencies[name] = param.default
                continue

            # Ошибка для обязательных параметров
            raise ValueError(f"Can't resolve parameter '{name}' for {impl}")

        return impl(**dependencies)

    def scope(self):
        return ScopeContext(self)


class ScopeContext:
    def __init__(self, injector: Injector):
        self.injector = injector

    def __enter__(self):
        self.injector.enter_scope()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.injector.exit_scope()
        return False


# ================== Пример использования ==================
class ILogger:
    def log(self, message: str):
        pass


class IDataService:
    def fetch_data(self) -> str:
        pass


class IProcessor:
    def process(self, data: str) -> str:
        pass


# Реализации
class ConsoleLogger(ILogger):
    def log(self, message: str):
        print(f"[CONSOLE] {message}")


class FileLogger(ILogger):
    def __init__(self, filename: str = "app.log"):
        self.filename = filename

    def log(self, message: str):
        with open(self.filename, "a") as f:
            f.write(f"{message}\n")


class DebugDataService(IDataService):
    def fetch_data(self) -> str:
        return "Debug data"


class ProductionDataService(IDataService):
    def __init__(self, logger: ILogger):
        self.logger = logger

    def fetch_data(self) -> str:
        self.logger.log("Fetching production data")
        return "Sensitive production data"


class SimpleProcessor(IProcessor):
    def process(self, data: str) -> str:
        return f"Processed: {data}"


class AdvancedProcessor(IProcessor):
    def __init__(self, logger: ILogger):
        self.logger = logger

    def process(self, data: str) -> str:
        self.logger.log(f"Processing: {data}")
        return f"ADVANCED: {data.upper()}"


# Конфигурации
def configure_debug(injector: Injector):
    injector.register(ILogger, ConsoleLogger, LifeStyle.SINGLETON)
    injector.register(IDataService, DebugDataService, LifeStyle.PER_REQUEST)
    injector.register(IProcessor, SimpleProcessor, LifeStyle.SCOPED)


def configure_production(injector: Injector):
    injector.register(ILogger, lambda: FileLogger("prod.log"), LifeStyle.SINGLETON)
    injector.register(IDataService, ProductionDataService, LifeStyle.SCOPED)
    injector.register(IProcessor, AdvancedProcessor, LifeStyle.SCOPED)


# Демонстрация
def demo(injector: Injector):
    print("\n===== Global Scope =====")
    logger = injector.get_instance(ILogger)
    logger.log("Global scope message")

    with injector.scope():
        print("\n===== Scope 1 =====")
        data_service = injector.get_instance(IDataService)
        processor = injector.get_instance(IProcessor)

        data = data_service.fetch_data()
        result = processor.process(data)
        logger.log(f"Result 1: {result}")

        same_data_service = injector.get_instance(IDataService)
        print(f"Same data_service? {data_service is same_data_service}")

    with injector.scope():
        print("\n===== Scope 2 =====")
        new_data_service = injector.get_instance(IDataService)
        new_processor = injector.get_instance(IProcessor)

        data = new_data_service.fetch_data()
        result = new_processor.process(data)
        logger.log(f"Result 2: {result}")

    print("\n===== Global Scope Again =====")
    same_logger = injector.get_instance(ILogger)
    print(f"Same logger? {logger is same_logger}")


if __name__ == "__main__":
    # Конфигурация Debug
    debug_injector = Injector()
    configure_debug(debug_injector)
    print("=== DEBUG CONFIGURATION ===")
    demo(debug_injector)

    # Конфигурация Production
    prod_injector = Injector()
    configure_production(prod_injector)
    print("\n\n=== PRODUCTION CONFIGURATION ===")
    demo(prod_injector)
