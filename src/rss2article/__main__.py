from .logging import setup_logging
from .main import main

setup_logging()
raise SystemExit(main())
