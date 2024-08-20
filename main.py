import os
import sys
import time
import json
import logging
import platform
import subprocess
import psutil
import requests


# setup loggers
logger = logging.getLogger(__name__)
logging.basicConfig(format="(%(asctime)s) %(message)s")
logger.setLevel(logging.INFO)

# BetterDiscord URL
BD_ASAR_URL = "https://github.com/rauenzi/BetterDiscordApp/releases/latest/download/betterdiscord.asar"

# MacOS-specific paths
HOME_DIR = os.path.expanduser("~")
BD_PARENT_PATH = os.path.join(HOME_DIR, "Library/Application Support/BetterDiscord")
DISCORD_PARENT_PATH = os.path.join(HOME_DIR, "Library/Application Support/discord")


BD_ASAR_SAVE_PATH = os.path.join(BD_PARENT_PATH, "data/betterdiscord.asar")


# load settings
CURRENT_SETTINGS_VERSION = 2
LAST_INSTALLED_DISCORD_VERSION = None


def start_discord():
    subprocess.Popen(["open", "-a", "Discord"])


def getInstalledDiscordVersion(DISCORD_PARENT_PATH: str) -> str:
    # On MacOS, the discord version is set as a folder within Library/Application Support/discord --> ex. 0.0.315

    # gets all versions of discord installed
    discord_path = [
        i for i in os.listdir(DISCORD_PARENT_PATH) if i.replace(".", "").isdigit()
    ]
    discord_path.sort()
    latest_installed_discord_version = discord_path[-1]
    discord_path = os.path.join(DISCORD_PARENT_PATH, latest_installed_discord_version)
    return discord_path


def set_discord_index_js_path(discord_path: str) -> str:
    index_js_path = os.path.join(discord_path, "modules/discord_desktop_core/index.js")
    return index_js_path


def patch_discord_index_js(discord_index_js_path: str, bd_asar_save_path: str) -> None:
    # Open the index.js file
    logger.info("Patching Discord index file to use BetterDiscord...")
    with open(discord_index_js_path, "r+") as file:
        content = file.read()
        logger.info(f"Updating Discord index at: {discord_index_js_path}")
        if "betterdiscord.asar" not in content:
            # Insert the require line at the top
            content = f'require("{bd_asar_save_path}");\n' + content
            file.seek(0)
            file.write(content)
            file.truncate()
    logger.info("Patching Discord index file.")


def download_betterdiscord_asar(asar_url: str, bd_asar_save_path: str) -> None:
    logger.info("Downloading latest BetterDiscord asar file...")
    response = requests.get(asar_url)

    logger.info("Updating local BetterDiscord asar file with latest...")
    with open(bd_asar_save_path, "wb") as file:
        logger.info(f"Saving to: {bd_asar_save_path}")
        file.write(response.content)

    logger.info("BetterDiscord asar file updated.")


# Mac is Darwin
if platform.system() != "Darwin":
    input(
        "Your system is not supported yet to using this script\n"
        "\n"
        "Press ENTER to exit."
    )
    sys.exit(1)


if __name__ == "__main__":

    logger.info("BetterDiscordAutoInstaller v1.2.0")
    logger.info(
        f""" Paths:
        HOME_DIR: {HOME_DIR}
        BD_PATH: {BD_PARENT_PATH}
        BD_ASAR_SAVE_PATH: {BD_ASAR_SAVE_PATH}
        DISCORD_PARENT_PATH: {DISCORD_PARENT_PATH}
        """
    )

    discord_version_path = getInstalledDiscordVersion(DISCORD_PARENT_PATH)
    discord_index_js_path = set_discord_index_js_path(discord_version_path)

    patch_discord_index_js(discord_index_js_path, BD_ASAR_SAVE_PATH)
    download_betterdiscord_asar(BD_ASAR_URL, BD_ASAR_SAVE_PATH)
