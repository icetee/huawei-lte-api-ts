import datetime
from typing import Optional, Tuple, Union
from urllib.parse import urlparse, urlunparse
from huawei_lte_api.Connection import Connection


class AuthorizedConnection(Connection):
    LOGOUT_TIMEOUT = 300  # seconds
    login_time = None
    logged_in = False

    def __init__(self, url: str, username: Optional[str]=None, password: Optional[str]=None, timeout: Union[float, Tuple[float, float], None] = None):
        # Auth info embedded in the URL may reportedly cause problems, strip it
        parsed_url = urlparse(url)
        clear_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc.rpartition("@")[-1],
            *parsed_url[2:]
        ))
        super().__init__(clear_url, timeout=timeout)
        username = username if username else parsed_url.username
        password = password if password else parsed_url.password

        from huawei_lte_api.api.User import User  # pylint: disable=cyclic-import,import-outside-toplevel
        self.user = User(self, username, password)

        if self.user.login(True):
            self.login_time = datetime.datetime.utcnow()
            self.logged_in = True

    def _is_login_timeout(self) -> bool:
        if self.login_time is None:
            return True
        logout_time = self.login_time + datetime.timedelta(seconds=self.LOGOUT_TIMEOUT)
        return logout_time < datetime.datetime.utcnow()