import pytest

from giramatch import auth


@pytest.fixture(autouse=True)
def _zerar_limite_de_login():
    """O limite de tentativas e global no processo: zera antes de cada teste para eles nao se influenciarem."""
    auth.limpar_falhas_login()
    yield
    auth.limpar_falhas_login()
