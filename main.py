import sys
from cli import runCli

if __name__ == "__main__":
    adminMode = "admin" in sys.argv
    debug = "debug" in sys.argv
    try:
        runCli(adminMode=adminMode, debug=debug)
    except KeyboardInterrupt:
        print()