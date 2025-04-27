import json, re, requests, webbrowser, platform, os
from customtkinter import *
from tkinter import BOTH, Text, Toplevel, filedialog, messagebox
from lib.CTkMenuBar import *
from lib.CTkToolTip import *
from lib.decrypt import decrypt_es3
from lib.encrypt import encrypt_es3
from datetime import datetime
from xml.etree import ElementTree
from PIL import Image
from pathlib import Path

DEBUGLEVEL = None

if DEBUGLEVEL:
    import logging
    logging.basicConfig(level=DEBUGLEVEL)
    ui_logger = logging.getLogger("customtkinter")
    ui_logger.setLevel(DEBUGLEVEL)
    logger = logging.getLogger(__name__)
    logger.setLevel(DEBUGLEVEL)

CACHE_DIR = Path.home() / ".cache" / "noedl.xyz"
CACHE_DIR.mkdir(parents=True, exist_ok=True) 

if DEBUGLEVEL:
    logger.info("Cache directory created.")

version = "1.0.1"
json_data = {}
savefile_dir = Path.home() / "AppData" / "LocalLow" / "semiwork" / "Repo" / "saves"

if DEBUGLEVEL:
    logger.info("Save file directory set. Path: " + str(savefile_dir))

def resource_path(relative_path):
    """ Get the absolute path to resources (for PyInstaller compatibility) """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

root = CTk()
root.geometry("900x540")
root.title("R.E.P.O Save Editor")

# Set application icon
icon_path = resource_path("icon.ico")
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)
    if DEBUGLEVEL:
        logger.info(f"Set application icon from: {icon_path}")
else:
    if DEBUGLEVEL:
        logger.warning(f"Icon file not found at: {icon_path}")

set_appearance_mode("dark")
set_default_color_theme("dark-blue")

font = ("Arial", 12)
small_font = ("Arial", 9)

if platform.system() == "Windows":
    menu = CTkTitleMenu(master=root)
else:
    menu = CTkMenuBar(master=root)

button_file = menu.add_cascade("File")
button_help = menu.add_cascade("Help")
dropdown1 = CustomDropdownMenu(widget=button_file)
dropdown1.add_option(option="Open", command=lambda: open_file())
dropdown2 = CustomDropdownMenu(widget=button_help)

dropdown2.add_option(option="How to Use", command=lambda: webbrowser.open("https://github.com/thaovd/R.E.P.O-Save-Editor#how-to-use"))
dropdown2.add_option(option="About", command=lambda: webbrowser.open("https://github.com/thaovd/R.E.P.O-Save-Editor"))
dropdown2.add_option(option="Report Issue", command=lambda: webbrowser.open("https://github.com/thaovd/R.E.P.O-Save-Editor/issues/new"))

label = CTkLabel(root, text="No data loaded.", font=font)
label.pack(fill=BOTH, expand=True)

# Simple footer with version info, no update checking
label_footer = CTkLabel(root, text=f"Version: {version}, Copyright © {datetime.now().year} noedl.xyz & vuthao.id.vn", font=small_font, text_color="gray30")
label_footer.pack(side="bottom", pady=5)

players = []
player_entries = {}
item_entries = {}  # Dictionary to store item entry widgets

def create_entry(label, parent, color, update_callback=None, tooltip=None):
    frame = CTkFrame(parent, fg_color=color)
    frame.pack(fill="x", pady=3)
    CTkLabel(frame, text=label, font=font).pack(side="left", padx=5)
    entry = CTkEntry(frame, font=font, width=100, border_color='#303030', fg_color="#292929")
    entry.pack(side="right", padx=5)
    if tooltip:
        CTkToolTip(frame, tooltip)
    if update_callback:
        entry.bind("<KeyRelease>", update_callback)
    if DEBUGLEVEL:
        ui_logger.info(f"Creating entry field for: {label}")
    return entry

def highlight_json():
        """ Highlights JSON syntax in the text widget. """
        textbox.tag_remove("key", "1.0", "end")
        textbox.tag_remove("string", "1.0", "end")
        textbox.tag_remove("number", "1.0", "end")
        textbox.tag_remove("boolean", "1.0", "end")

        json_text = textbox.get("1.0", "end-1c")

        key_pattern = r'(\"[^\"]*\")\s*:'
        string_pattern = r'(:\s*)("(?:\\.|[^"\\])*")'
        number_pattern = r'(:\s*)(\d+(\.\d+)?)'
        boolean_pattern = r'(:\s*)(true|false|null)'

        for match in re.finditer(key_pattern, json_text):
            start, end = f"1.0+{match.start()}c", f"1.0+{match.end(1)}c"
            textbox.tag_add("key", start, end)

        for match in re.finditer(string_pattern, json_text):
            start, end = f"1.0+{match.start(2)}c", f"1.0+{match.end(2)}c"
            textbox.tag_add("string", start, end)

        for match in re.finditer(number_pattern, json_text):
            start, end = f"1.0+{match.start(2)}c", f"1.0+{match.end(2)}c"
            textbox.tag_add("number", start, end)

        for match in re.finditer(boolean_pattern, json_text):
            start, end = f"1.0+{match.start(2)}c", f"1.0+{match.end(2)}c"
            textbox.tag_add("boolean", start, end)
        
        if DEBUGLEVEL:
            ui_logger.info("JSON syntax highlighted.")

def update_json_data(event):
    if entry_level.get() == "" or entry_currency.get() == "" or entry_lives.get() == "" or entry_charging.get() == "" or entry_haul.get() == "" or entry_teamname.get() == "":
        if DEBUGLEVEL:
            ui_logger.info("Failed to update JSON data. One or more fields are empty.")
        return
    else:
        print(entry_level.get(), entry_currency.get(), entry_lives.get(), entry_charging.get(), entry_haul.get(), entry_teamname.get())
        json_data['dictionaryOfDictionaries']['value']['runStats']['level'] = int(entry_level.get())
        json_data['dictionaryOfDictionaries']['value']['runStats']['currency'] = int(entry_currency.get())
        json_data['dictionaryOfDictionaries']['value']['runStats']['lives'] = int(entry_lives.get())
        json_data['dictionaryOfDictionaries']['value']['runStats']['chargingStationCharge'] = int(entry_charging.get())
        json_data['dictionaryOfDictionaries']['value']['runStats']['totalHaul'] = int(entry_haul.get())
        json_data['teamName']['value'] = entry_teamname.get()
    
    # Update players
    for player in players:
        player_name = player['name']
        player_id = player['id']
        

        # Update player health
        if f"{player_name}_health" in player_entries and player_entries[f"{player_name}_health"].get():
            json_data["dictionaryOfDictionaries"]["value"]["playerHealth"][player_id] = int(player_entries[f"{player_name}_health"].get())
        print(f"Checking player: {player_name} (ID: {player_id})")
        print(f"Health for {player_name}: {player_entries[f'{player_name}_health'].get()}")
        # Update player upgrades
        if f"{player_name}_health_upgrade" in player_entries and player_entries[f"{player_name}_health_upgrade"].get():
            json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeHealth"][player_id] = int(player_entries[f"{player_name}_health_upgrade"].get())
        
        if f"{player_name}_stamina_upgrade" in player_entries and player_entries[f"{player_name}_stamina_upgrade"].get():
            json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeStamina"][player_id] = int(player_entries[f"{player_name}_stamina_upgrade"].get())
        
        if f"{player_name}_extra_jump_upgrade" in player_entries and player_entries[f"{player_name}_extra_jump_upgrade"].get():
            json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeExtraJump"][player_id] = int(player_entries[f"{player_name}_extra_jump_upgrade"].get())
        
        if f"{player_name}_launch_upgrade" in player_entries and player_entries[f"{player_name}_launch_upgrade"].get():
            json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeLaunch"][player_id] = int(player_entries[f"{player_name}_launch_upgrade"].get())
        
        if f"{player_name}_mapplayercount_upgrade" in player_entries and player_entries[f"{player_name}_mapplayercount_upgrade"].get():
            json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeMapPlayerCount"][player_id] = int(player_entries[f"{player_name}_mapplayercount_upgrade"].get())
        
        # Fix the variable names for these upgrades
        if f"{player_name}_speed_upgrade" in player_entries and player_entries[f"{player_name}_speed_upgrade"].get():
            json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeSpeed"][player_id] = int(player_entries[f"{player_name}_speed_upgrade"].get())
        
        if f"{player_name}_strength_upgrade" in player_entries and player_entries[f"{player_name}_strength_upgrade"].get():
            json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeStrength"][player_id] = int(player_entries[f"{player_name}_strength_upgrade"].get())
        
        if f"{player_name}_range_upgrade" in player_entries and player_entries[f"{player_name}_range_upgrade"].get():
            json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeRange"][player_id] = int(player_entries[f"{player_name}_range_upgrade"].get())
        
        if f"{player_name}_throw_upgrade" in player_entries and player_entries[f"{player_name}_throw_upgrade"].get():
            json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeThrow"][player_id] = int(player_entries[f"{player_name}_throw_upgrade"].get())
        
        if DEBUGLEVEL:
            logger.info(f"Updated player {player_name} (ID: {player_id}) data")
    
    # Update items
    if 'itemsPurchased' in json_data['dictionaryOfDictionaries']['value']:
        for item_name, entry_widget in item_entries.items():
            if entry_widget.get():
                try:
                    json_data['dictionaryOfDictionaries']['value']['itemsPurchased'][item_name] = int(entry_widget.get())
                except ValueError:
                    if DEBUGLEVEL:
                        ui_logger.error(f"Invalid value for item {item_name}: {entry_widget.get()}")
    
    textbox.delete("1.0", "end")
    textbox.insert("1.0", json.dumps(json_data, indent=4))
    if DEBUGLEVEL:
        ui_logger.info("JSON data updated.")
        logger.info("JSON data: " + json.dumps(json_data, indent=4))
    highlight_json()

def on_json_edit(event):
    """ Updates the UI fields when the JSON editor is modified. """
    global json_data
    try:
        updated_data = json.loads(textbox.get("1.0", "end-1c"))

        entry_level.delete(0, "end")
        entry_level.insert(0, updated_data['dictionaryOfDictionaries']['value']['runStats']['level'])

        entry_currency.delete(0, "end")
        entry_currency.insert(0, updated_data['dictionaryOfDictionaries']['value']['runStats']['currency'])

        entry_lives.delete(0, "end")
        entry_lives.insert(0, updated_data['dictionaryOfDictionaries']['value']['runStats']['lives'])

        entry_charging.delete(0, "end")
        entry_charging.insert(0, updated_data['dictionaryOfDictionaries']['value']['runStats']['chargingStationCharge'])

        entry_haul.delete(0, "end")
        entry_haul.insert(0, updated_data['dictionaryOfDictionaries']['value']['runStats']['totalHaul'])

        entry_teamname.delete(0, "end")
        entry_teamname.insert(0, updated_data['teamName']['value'])

        for player in players:
            player_name = player['name']
            player_id = player['id']

            print(f"Checking player: {player_name} (ID: {player_id})")

            if player_id in updated_data['dictionaryOfDictionaries']['value']['playerHealth']:
                health_value = updated_data['dictionaryOfDictionaries']['value']['playerHealth'][player_id]
                print(f"Health for {player_name}: {health_value}")

                if f"{player_name}_health" in player_entries:
                    print(f"Updating UI for {player_name}")
                    player_entries[f"{player_name}_health"].delete(0, "end")
                    player_entries[f"{player_name}_health"].insert(0, health_value)
                else:
                    print(f"Entry field missing for {player_name}_health")
            else:
                print(f"Player ID {player_id} not found in playerHealth")

        # Update item counts
        if 'itemsPurchased' in updated_data['dictionaryOfDictionaries']['value']:
            for item_name, count in updated_data['dictionaryOfDictionaries']['value']['itemsPurchased'].items():
                if item_name in item_entries:
                    item_entries[item_name].delete(0, "end")
                    item_entries[item_name].insert(0, count)

        json_data = updated_data
        highlight_json()
    
        if DEBUGLEVEL:
            ui_logger.info("JSON data updated from editor.")
    except json.JSONDecodeError:
        if DEBUGLEVEL:
            ui_logger.error("Failed to update JSON data from editor.")
        pass

def open_file():
    global json_data
    global savefilename
    file_path = filedialog.askopenfilename(initialdir=savefile_dir, filetypes=[("Game Save (.es3 file)", "*.es3")])
    if file_path:        
        decrypted_data = decrypt_es3(file_path, "Why would you want to cheat?... :o It's no fun. :') :'D")
        json_data = json.loads(decrypted_data)
        update_ui_from_json(json_data)
        savefilename = Path(file_path).name
        messagebox.showinfo("File Opened", f"Successfully opened: {file_path}")
        if DEBUGLEVEL:
            ui_logger.info(f"File opened: {file_path}")
    else:
        if DEBUGLEVEL:
            ui_logger.error("Failed to open file.")

def save_data():
    if not json_data:
        messagebox.showerror("Error", "No data to save.")
        if DEBUGLEVEL:
            ui_logger.error("No data to save.")
        return

    file_path = filedialog.asksaveasfilename(initialdir=savefile_dir, initialfile=savefilename, defaultextension=".es3", filetypes=[("Game Save (.es3 file)", "*.es3")])
    if file_path:
        encrypted_data = encrypt_es3(json.dumps(json_data, indent=4).encode('utf-8'), "Why would you want to cheat?... :o It's no fun. :') :'D")
        with open(file_path, 'wb') as f:
            f.write(encrypted_data)
        messagebox.showinfo("File Saved", f"Successfully saved: {file_path}")
        if DEBUGLEVEL:
            ui_logger.info(f"File saved: {file_path}")
    else:
        if DEBUGLEVEL:
            ui_logger.error("Failed to save file.")

def create_items_ui(parent, items_data):
    """Create UI elements for items management"""
    global item_entries
    item_entries.clear()
    
    # Group items by category
    item_categories = {
        "Cart": [],
        "Drone": [],
        "Extraction": [],
        "Grenade": [],
        "Gun": [],
        "Health": [],
        "Melee": [],
        "Mine": [],
        "Orb": [],
        "Power": [],
        "Rubber": [],
        "Upgrade": [],
        "Valuable": []
    }
    
    for item_name in items_data.keys():
        for category in item_categories.keys():
            if category.lower() in item_name.lower():
                item_categories[category].append(item_name)
                break
    
    # Create notebook for item categories
    items_notebook = CTkTabview(parent, height=300)
    items_notebook.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Create a tab for each category that has items
    for category, items in item_categories.items():
        if items:
            tab = items_notebook.add(category)
            frame = CTkScrollableFrame(tab)
            frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Create entries for each item
            for item_name in sorted(items):
                item_entry = create_entry(item_name.replace("Item ", ""), frame, "#292929", update_json_data)
                item_entry.insert(0, items_data.get(item_name, 0))
                item_entries[item_name] = item_entry

def update_ui_from_json(data):
    global players, player_entries
    players.clear()
    player_entries.clear()

    dropdown1.add_option(option="Save", command=lambda: save_data())
    dropdown1.add_separator()
    sub_menu = dropdown1.add_submenu("Export As (Currently Unavailable)")
    sub_menu.add_option(option=".TXT (Currently Unavailable)", command=lambda: messagebox.showinfo("Error", "I told you it's not available yet. :)"))
    sub_menu.add_option(option=".JSON (Currently Unavailable)", command=lambda: messagebox.showinfo("Error", "I told you it's not available yet. :)"))
    
    tabview = CTkTabview(root, width=680, height=400)
    tabview.pack(fill=BOTH, expand=True)
    tabview.add("World")
    tabview.add("Player")
    tabview.add("Advanced")
    
    frame_world = CTkFrame(tabview.tab("World"))
    frame_world.pack(fill=BOTH, expand=True, padx=10, pady=10)
    
    global entry_level, entry_currency, entry_lives, entry_charging, entry_haul, entry_teamname
    entry_level = create_entry("Level:", frame_world, "#292929", update_json_data, "The level of the game.")
    entry_currency = create_entry("Currency:", frame_world, "#292929", update_json_data, "The amount of currency the game has. In thousands.")
    entry_lives = create_entry("Lives:", frame_world, "#292929", update_json_data, "The amount of lives the game has.")
    entry_charging = create_entry("Charging Station Charge's:", frame_world, "#292929", update_json_data, "The amount of charge the charging station has.")
    entry_haul = create_entry("Total Haul:", frame_world, "#292929", update_json_data, "The total haul of the game.")
    entry_teamname = create_entry("Team Name:", frame_world, "#292929", update_json_data, "The name of the team.")

    entry_level.insert(0, data['dictionaryOfDictionaries']['value']['runStats']['level'])
    entry_currency.insert(0, data['dictionaryOfDictionaries']['value']['runStats']['currency'])
    entry_lives.insert(0, data['dictionaryOfDictionaries']['value']['runStats']['lives'])
    entry_charging.insert(0, data['dictionaryOfDictionaries']['value']['runStats']['chargingStationCharge'])
    entry_haul.insert(0, data['dictionaryOfDictionaries']['value']['runStats']['totalHaul'])
    entry_teamname.insert(0, data['teamName']['value'])

    frame_items = CTkFrame(frame_world, corner_radius=10)
    frame_items.pack(fill=BOTH, expand=True, pady=10)
    CTkLabel(frame_items, text="Items", font=font).pack(anchor="w", padx=10, pady=5)
    
    # Check if itemsPurchased exists in the data
    if 'itemsPurchased' in data['dictionaryOfDictionaries']['value']:
        create_items_ui(frame_items, data['dictionaryOfDictionaries']['value']['itemsPurchased'])
    else:
        CTkLabel(frame_items, text="No item data available", font=font, text_color="white").pack(fill=BOTH, expand=True)
    
    frame_player = CTkScrollableFrame(tabview.tab("Player"))
    frame_player.pack(fill=BOTH, expand=True, padx=10, pady=10)
    
    for player_id, player_name in data["playerNames"]["value"].items():
        player_health = data["dictionaryOfDictionaries"]["value"]["playerHealth"][player_id]
        players.append({"id": player_id, "name": player_name, "health": player_health})
    
    def fetch_steam_profile_picture(player_id):
        """Fetch and cache Steam profile picture in the cache folder."""
        cached_image_path = CACHE_DIR / f"{player_id}.png"
        if cached_image_path.exists():
            return str(cached_image_path)

        url = f"https://steamcommunity.com/profiles/{player_id}/?xml=1"
        response = requests.get(url)
        if response.status_code == 200:
            tree = ElementTree.fromstring(response.content)
            avatar_icon = tree.find('avatarIcon')
            if avatar_icon is not None:
                img_url = avatar_icon.text
                img_data = requests.get(img_url).content
                with open(cached_image_path, 'wb') as file:
                    file.write(img_data)
                if DEBUGLEVEL:
                    ui_logger.info(f"Steam profile picture for player ID: {player_id} fetched and cached.")
                return str(cached_image_path)
            
        if DEBUGLEVEL:
            ui_logger.error(f"Failed to fetch Steam profile picture for player ID: {player_id}")
        return resource_path("example.png")  # Fallback to a default image
    
    for player in players:
        frame = CTkFrame(frame_player, corner_radius=6, fg_color="#292929")
        frame.pack(fill="x", pady=3)

        profile_picture_path = fetch_steam_profile_picture(player['id'])

        image = Image.open(profile_picture_path)
        my_image = CTkImage(light_image=image, dark_image=image, size=(30, 30))
        image_label = CTkLabel(frame, image=my_image, text="")
        image_label.pack(side="left", anchor="nw", padx=(10, 5), pady=10)
        
        CTkLabel(frame, text=player['name'], font=font).pack(anchor="w", padx=5, pady=[5, 0])

        health_entry = create_entry("Health:", frame, "#292929", update_json_data, "The amount of health the player has. Max 200.")
        health_entry.insert(0, player['health'])
        player_entries[f"{player['name']}_health"] = health_entry

        CTkLabel(frame, text="Upgrades: ", font=font).pack(anchor="w")        
        CTkFrame(frame, width=frame.winfo_width()-10, height=2, fg_color='gray25').pack(fill="x", pady=5)

        health_upgrade_entry = create_entry("Health:", frame, "#292929", update_json_data)
        health_upgrade_entry.insert(0, data['dictionaryOfDictionaries']['value']['playerUpgradeHealth'][player['id']])
        player_entries[f"{player['name']}_health_upgrade"] = health_upgrade_entry

        stamina_upgrade_entry = create_entry("Stamina:", frame, "#292929", update_json_data)
        stamina_upgrade_entry.insert(0, data['dictionaryOfDictionaries']['value']['playerUpgradeStamina'][player['id']])
        player_entries[f"{player['name']}_stamina_upgrade"] = stamina_upgrade_entry
        
        extra_jump_entry = create_entry("Extra Jump:", frame, "#292929", update_json_data)
        extra_jump_entry.insert(0, data['dictionaryOfDictionaries']['value']['playerUpgradeExtraJump'][player['id']])
        player_entries[f"{player['name']}_extra_jump_upgrade"] = extra_jump_entry

        lauch_upgrade_entry = create_entry("Launch:", frame, "#292929", update_json_data)
        lauch_upgrade_entry.insert(0, data['dictionaryOfDictionaries']['value']['playerUpgradeLaunch'][player['id']])
        player_entries[f"{player['name']}_launch_upgrade"] = lauch_upgrade_entry

        mapplayercount_upgrade_entry = create_entry("Map Player Count:", frame, "#292929", update_json_data)
        mapplayercount_upgrade_entry.insert(0, data['dictionaryOfDictionaries']['value']['playerUpgradeMapPlayerCount'][player['id']])
        player_entries[f"{player['name']}_mapplayercount_upgrade"] = mapplayercount_upgrade_entry

        # In update_ui_from_json function, replace these lines:
        speed_upgrade_entry = create_entry("Speed:", frame, "#292929", update_json_data)
        speed_upgrade_entry.insert(0, data['dictionaryOfDictionaries']['value']['playerUpgradeSpeed'][player['id']])
        player_entries[f"{player['name']}_speed_upgrade"] = speed_upgrade_entry
        
        strength_upgrade_entry = create_entry("Strength:", frame, "#292929", update_json_data)
        strength_upgrade_entry.insert(0, data['dictionaryOfDictionaries']['value']['playerUpgradeStrength'][player['id']])
        player_entries[f"{player['name']}_strength_upgrade"] = strength_upgrade_entry
        
        range_upgrade_entry = create_entry("Range:", frame, "#292929", update_json_data)
        range_upgrade_entry.insert(0, data['dictionaryOfDictionaries']['value']['playerUpgradeRange'][player['id']])
        player_entries[f"{player['name']}_range_upgrade"] = range_upgrade_entry
        
        throw_upgrade_entry = create_entry("Throw:", frame, "#292929", update_json_data)
        throw_upgrade_entry.insert(0, data['dictionaryOfDictionaries']['value']['playerUpgradeThrow'][player['id']])
        player_entries[f"{player['name']}_throw_upgrade"] = throw_upgrade_entry

        if DEBUGLEVEL:
            ui_logger.info(f"Player {player['name']} UI created.")


    frame_advanced = CTkFrame(tabview.tab("Advanced"), corner_radius=10)
    frame_advanced.pack(fill=BOTH, expand=True, padx=10, pady=10)
    CTkLabel(frame_advanced, text="Edit JSON:", font=font).pack(anchor="w", padx=5, pady=3)
    
    global textbox
    textbox = Text(frame_advanced, font=("Courier", 10), height=12, wrap="word", bg="#2b2b2b", fg="white", bd=0, highlightthickness=0, insertbackground="white")
    textbox.pack(fill=BOTH, expand=True, padx=5, pady=5)
    textbox.insert("1.0", json.dumps(json_data, indent=4))
    
    textbox.tag_configure("key", foreground="#e06c69")      # Keys
    textbox.tag_configure("string", foreground="#7ac379")   # Strings
    textbox.tag_configure("number", foreground="#d19a5d")   # Numbers
    textbox.tag_configure("boolean", foreground="#66CCFF")  # Booleans

    highlight_json()
    textbox.bind("<KeyRelease>", on_json_edit)
    label.pack_forget()

    if DEBUGLEVEL:
        ui_logger.info("UI updated from JSON data.")

root.mainloop()