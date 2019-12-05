__all__ = ["authenticate", "pipelines"]

from .authentication import authenticate

import os
def reset():
    """Reset the run time if you are actively working on some code."""
    os.kill(os.getpid(), 9)
    os.popen("rm -rf /usr/local/lib/python3.6/dist-packages/carsmoney/__pycache__")
