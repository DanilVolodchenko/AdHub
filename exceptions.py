class UpdateRoleError(Exception):
    """Администратор не может менять права администратора."""
    pass


class TokenError(Exception):
    """Не верный токен."""
    pass