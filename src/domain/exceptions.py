class DomainException(Exception):
    """Базовое исключение для доменной логики."""
    @property
    def message(self) -> str:
        return "Произошла неизвестная ошибка"

class Forbidden(DomainException):
    @property
    def message(self) -> str:
        return "Недостаточно прав для выполнения операции"

class SessionHasExpired(DomainException):
    @property
    def message(self) -> str:
        return "Сессия устарела или была завершена"

class UserNotFound(DomainException):
    @property
    def message(self) -> str:
        return "Пользователь не найден"

class UserEmailAlreadyExists(DomainException):
    @property
    def message(self) -> str:
        return "Пользователь с таким email или именем уже существует"

class UsernameAlreadyExists(DomainException):
    @property
    def message(self) -> str:
        return "Пользователь с таким email или именем уже существует"

class InvalidVerifyCode(DomainException):
    @property
    def message(self) -> str:
        return "Неверный код"

class VerifyCodeNotConfirmed(DomainException):
    @property
    def message(self) -> str:
        return "Проверочный код не подтвержден"

class CodeHasExpired(DomainException):
    @property
    def message(self) -> str:
        return "Код был просрочен"
