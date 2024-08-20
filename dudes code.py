
if os.path.exists(BD_SETTINGS_PATH):
    try:
        settings: dict = json.load(open(BD_SETTINGS_PATH))
    except json.JSONDecodeErrorBD_:
        logger.info("Settings were corrupted. Using default values")
    else:
        settings_version = settings.get("settings_version")
        if (
            settings_version is None
        ):  # first version of settings (settings_version just was not saved xd)
            DISCORD_PARENT_PATH = settings.get("discord_installed_path")
        elif settings_version == 2:
            DISCORD_PARENT_PATH = settings.get("discord_installed_path")
            LAST_INSTALLED_DISCORD_VERSION = settings.get(
                "last_installed_discord_version"
            )

# determining the latest installed version of discord
discord_path = [
    i for i in os.listdir(DISCORD_PARENT_PATH) if i.startswith("app-")
]  # remove all not 'app-' items
discord_path.sort()
latest_installed_discord_version = discord_path[
    -1
]  # the oldest version will be the last of list
discord_path = os.path.join(DISCORD_PARENT_PATH, latest_installed_discord_version)

# get discord location from user if it is not valid
while True:
    if not os.path.exists(os.path.join(DISCORD_PARENT_PATH, "update.exe")):
        logger.info(
            f'Discord was not found at "{DISCORD_PARENT_PATH}". Enter the dir to folder with "Update.exe":'
        )
        DISCORD_PARENT_PATH = input("\n=> ")

        json.dump(
            {
                "settings_version": CURRENT_SETTINGS_VERSION,
                "discord_installed_path": DISCORD_PARENT_PATH,
                "last_installed_discord_version": LAST_INSTALLED_DISCORD_VERSION,
            },
            open(BD_SETTINGS_PATH, "w"),
        )
    else:
        break

if latest_installed_discord_version == LAST_INSTALLED_DISCORD_VERSION:
    logger.info(
        "Discord is up to date, patching is not needed. Exiting in 3 seconds..."
    )
    time.sleep(3)
    sys.exit(0)

# The "--service-sandbox-type=audio" argument will only be in the
# updated discord instance, so it won't be in the update module

is_discord_running = False
is_discord_updating = True

# checking for currently updating discord
for process in psutil.process_iter(["name"]):
    if process.info.get("name") == "Discord.exe":
        is_discord_running = True

        try:
            for arg in process.cmdline():
                if "--service-sandbox-type=audio" in arg:
                    is_discord_updating = False
        except psutil.NoSuchProcess:
            pass

if is_discord_running and not is_discord_updating:
    logger.info("Discord is started and not updating. Killing discord...")

    for process in psutil.process_iter(["name"]):
        if process.info["name"] == "Discord.exe":
            try:
                process.kill()
            except psutil.NoSuchProcess:
                pass

    time.sleep(2)  # discord may not close instantly, so we need to wait for a while
    is_discord_running = False

# installing the latest version of discord
if not is_discord_running:
    start_discord()
    logger.info("Discord updater started")

logger.info("Waiting for finish of discord updating...")
quit_from_loop = False

while not quit_from_loop:
    for process in psutil.process_iter(["name"]):
        if quit_from_loop:
            break

        if process.info["name"] == "Discord.exe":
            try:
                for arg in process.cmdline():
                    if "--service-sandbox-type=audio" in arg:
                        time.sleep(5)  # wait 5 seconds to avoid any problematic shit
                        quit_from_loop = True
                        break
            except psutil.NoSuchProcess:
                pass

logger.info("Update finished. Patching...")
print()
time.sleep(0.1)

# patching
# determining the latest installed version of discord (after update)
discord_path = [
    i for i in os.listdir(DISCORD_PARENT_PATH) if i.startswith("app-")
]  # remove all not 'app-' items
discord_path.sort()
latest_installed_discord_version = discord_path[
    -1
]  # the oldest version will be the last of list
discord_path = os.path.join(DISCORD_PARENT_PATH, latest_installed_discord_version)

json.dump(
    {
        "settings_version": CURRENT_SETTINGS_VERSION,
        "discord_installed_path": DISCORD_PARENT_PATH,
        "last_installed_discord_version": latest_installed_discord_version,
    },
    open(BD_SETTINGS_PATH, "w"),
    )

for process in psutil.process_iter(["name"]):
    if process.info["name"] == "Discord.exe" and process.is_running():
        process.kill()
time.sleep(2)

index_js_path = os.path.join(
    discord_path, "modules/discord_desktop_core-1/discord_desktop_core/index.js"
)
bd_required_folders = [
    os.path.join(BD_PATH, ""),
    os.path.join(BD_PATH, "data"),
    os.path.join(BD_PATH, "themes"),
    os.path.join(BD_PATH, "plugins"),
]

# making folders
logger.info("Making folders...")

for folder in bd_required_folders:
    os.makedirs(folder, exist_ok=True)

logger.info("Folders have been made!")
print()
time.sleep(0.1)

# downloading betterdiscord asar
logger.info("Trying to download BetterDiscord asar file...")

while True:
    try:
        response = requests.get(BD_ASAR_URL)
    except requests.exceptions.ConnectionError:
        logger.info(f"Failed to download asar. Retrying in 3 seconds...")
        time.sleep(3)
    else:
        with open(BD_ASAR_SAVE_PATH, "wb") as file:
            file.write(response.content)
        break

logger.info("Asar has been successfully downloaded!")
print()
time.sleep(0.1)

# patching index.js
logger.info("Trying to patch discord startup script...")

with open(index_js_path, "rb") as file:
    content = file.readlines()

is_script_already_patched = [
    i for i in content if b"betterdiscord.asar" in i
]  # leaves lines that have 'betterdiscord.asar' in it
is_script_already_patched = bool(
    len(is_script_already_patched)
)  # this line should be only once in the file

if is_script_already_patched:
    logger.info("Script already patched!")
else:
    content.insert(0, f'require("{BD_ASAR_SAVE_PATH}");\n'.encode())

    with open(index_js_path, "wb") as file:
        file.writelines(content)

    logger.info("Patching finished!")
print()
time.sleep(0.1)

# start discord
start_discord()
logger.info("Discord has been started!")
print()
time.sleep(0.1)

logger.info("Installation finished!")
logger.info("Exiting in 3 seconds...")
time.sleep(3)
sys.exit(0)
