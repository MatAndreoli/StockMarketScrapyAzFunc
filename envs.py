import os
from tempfile import gettempdir

RUN_ENV = os.getenv("RUN_ENV", "")

FILE_PATH = f"{gettempdir()}/fiisdata.json" if RUN_ENV == "azure" else "fiisdata.json"
