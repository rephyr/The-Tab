import sys
from cli import runCli

if __name__ == "__main__":
    adminMode = "admin" in sys.argv
    debug = "debug" in sys.argv
    runCli(adminMode=adminMode, debug=debug)