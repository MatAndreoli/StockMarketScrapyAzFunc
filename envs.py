import os
from tempfile import gettempdir

RUN_ENV = os.getenv("RUN_ENV", "")

FILE_PATH = f"{gettempdir()}/" if RUN_ENV in ("azure", "aws") else ""
FIIS_FILE = f"{FILE_PATH}fiisdata.json"
STOCKS_FILE = f"{FILE_PATH}stocksdata.json"

