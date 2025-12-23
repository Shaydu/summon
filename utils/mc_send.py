import subprocess

MINECRAFT_SCREEN_NAME = "minecraft_server"

def send_command_to_minecraft(cmd: str) -> bool:
    """Send a command to the Minecraft Bedrock server via screen."""
    try:
        # The stuff command sends input to the screen session
        full_cmd = f'screen -S {MINECRAFT_SCREEN_NAME} -p 0 -X stuff "{cmd}\r"'
        result = subprocess.run(full_cmd, shell=True)
        return result.returncode == 0
    except Exception:
        return False
