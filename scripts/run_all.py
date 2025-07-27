import subprocess

subprocess.run(["python", "api-returns.py"], check=True)
subprocess.run(["python", "scrapper.py"], check=True)