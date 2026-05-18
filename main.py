import sys
from cli import runCli

if __name__ == "__main__":
    adminMode = len(sys.argv) > 1 and sys.argv[1] == "admin"
    runCli(adminMode=adminMode)