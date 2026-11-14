import subprocess

cmd = [
    "docker", "run", "--rm",
    "--name", "anti-spammer-bot",
    "-e", "BOT_TOKEN=<your discord bot token>",
    "-e", "PYTHONUNBUFFERED=1",   # see point 2
    "anti-spammer:1.0",
]

proc = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,   # merge stderr into stdout so you see both in order
    text=True,
    bufsize=1,                  # line-buffered on our side
)

for line in proc.stdout:
    print(line, end="", flush=True)

proc.wait()
print("------------return code------------")
print(proc.returncode)