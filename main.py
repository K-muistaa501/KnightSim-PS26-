```python
# -*- coding: utf-8 -*-
import pygame
import json
import os
import numpy as np
import random

# SAVE DATA

SAVE_FILE = "game_savedata.json"

DEFAULT_DATA = {
    "first_time": True,
    "opening_seen": False,
    "name": "",
    "class": "",
    "level": 1,
    "EXP": 0,
    "HP": 100,
    "AK": 15,
    "SP": 10,
    "DF": 10,
    "EP": 10,
    "geargrub_defeated": False
}

def load_save():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as file:
                saved = json.load(file)

            for key, value in DEFAULT_DATA.items():
                if key not in saved:
                    saved[key] = value

            return saved
        except (json.JSONDecodeError, OSError):
            print("Save file was invalid. Creating a new save.")

    save = DEFAULT_DATA.copy()

    with open(SAVE_FILE, "w", encoding="utf-8") as file:
        json.dump(save, file, indent=4)

    return save

def save_game():
    with open(SAVE_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def reset_save():
    global data, name, player_class, player_stats

    data = DEFAULT_DATA.copy()
    name = ""
    player_class = ""

    player_stats = {
        "HP": 100,
        "AK": 15,
        "SP": 10,
        "DF": 10,
        "EP": 10
    }

    save_game()

data = load_save()

name = data.get("name", "")
player_class = data.get("class", "")

player_stats = {
    "HP": data.get("HP", 100),
    "AK": data.get("AK", 15),
    "SP": data.get("SP", 10),
    "DF": data.get("DF", 10),
    "EP": data.get("EP", 10)
}

# HOW IT WORKS

# The save file stores the knight's progress.
# New values are automatically added if an older save is loaded.

# PYGAME SETUP

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((1600, 1200))
pygame.display.set_caption("KnightSim")

big_font = pygame.font.SysFont("DejaVu Sans Mono", 75)
normal_font = pygame.font.SysFont("DejaVu Sans Mono", 50)
small_font = pygame.font.SysFont("DejaVu Sans Mono", 35)
xsmall_font = pygame.font.SysFont("DejaVu Sans Mono", 15)

clock = pygame.time.Clock()

# MUSIC / SOUND

main_menu_music = "Sounds/KnightByte_OST_The_Quest_Main_menu.ogg"
settings_music = (
    "Sounds/dejcomin-deep-ambient-electronic-theme-music-"
    "loading-screen-menu-dejcoart-429846.ogg"
)
credits_music = "Sounds/pynchon.ogg"

menu_select_sound = pygame.mixer.Sound(
    "Sounds/freesound_community-menu-selection-102220.ogg"
)
pause_sound = pygame.mixer.Sound("Sounds/Pause_sound_game.ogg")
start_sound = pygame.mixer.Sound("Sounds/Start_sound_game.ogg")

muted = False
current_music = None

def make_higher(sound, amount=1.5):
    sound_array = pygame.sndarray.array(sound)

    if sound_array.ndim == 1:
        sound_array = sound_array.reshape(-1, 1)

    new_length = max(1, int(len(sound_array) / amount))
    new_indices = np.linspace(0, len(sound_array) - 1, new_length)

    new_sound_array = np.zeros(
        (new_length, sound_array.shape[1]),
        dtype=np.float64
    )

    for channel in range(sound_array.shape[1]):
        new_sound_array[:, channel] = np.interp(
            new_indices,
            np.arange(len(sound_array)),
            sound_array[:, channel]
        )

    new_sound_array = np.clip(
        new_sound_array,
        np.iinfo(sound_array.dtype).min,
        np.iinfo(sound_array.dtype).max
    ).astype(sound_array.dtype)

    return pygame.sndarray.make_sound(new_sound_array)

def make_lower(sound, amount=1.5):
    sound_array = pygame.sndarray.array(sound)

    if sound_array.ndim == 1:
        sound_array = sound_array.reshape(-1, 1)

    new_length = max(1, int(len(sound_array) * amount))
    new_indices = np.linspace(0, len(sound_array) - 1, new_length)

    new_sound_array = np.zeros(
        (new_length, sound_array.shape[1]),
        dtype=np.float64
    )

    for channel in range(sound_array.shape[1]):
        new_sound_array[:, channel] = np.interp(
            new_indices,
            np.arange(len(sound_array)),
            sound_array[:, channel]
        )

    new_sound_array = np.clip(
        new_sound_array,
        np.iinfo(sound_array.dtype).min,
        np.iinfo(sound_array.dtype).max
    ).astype(sound_array.dtype)

    return pygame.sndarray.make_sound(new_sound_array)

higher_menu_sound = make_higher(menu_select_sound)
lower_menu_sound = make_lower(menu_select_sound)

def play_sound(sound):
    if not muted and sound is not None:
        sound.play()

def update_mute():
    volume = 0 if muted else 1

    menu_select_sound.set_volume(volume)
    higher_menu_sound.set_volume(volume)
    lower_menu_sound.set_volume(volume)
    pause_sound.set_volume(volume)
    start_sound.set_volume(volume)
    pygame.mixer.music.set_volume(volume)

def K_ent_sound():
    play_sound(menu_select_sound)
    play_sound(higher_menu_sound)

def K_bks_sound():
    play_sound(menu_select_sound)
    play_sound(lower_menu_sound)

# HOW IT WORKS

# menu_select_sound is the normal menu sound.
# The higher and lower versions are used for ENTER and BACKSPACE.

# CLASSES

classes = {
    "Soldier": {
        "HP": 100,
        "AK": 15,
        "SP": 10,
        "DF": 10,
        "EP": 10
    },
    "Assassin": {
        "HP": 100,
        "AK": 15,
        "SP": 15,
        "DF": 5,
        "EP": 10
    },
    "Barbarian": {
        "HP": 125,
        "AK": 15,
        "SP": 5,
        "DF": 10,
        "EP": 10
    },
    "Archer": {
        "HP": 90,
        "AK": 20,
        "SP": 10,
        "DF": 10,
        "EP": 10
    },
    "Guardian": {
        "HP": 100,
        "AK": 15,
        "SP": 5,
        "DF": 15,
        "EP": 10
    },
    "Duelist": {
        "HP": 90,
        "AK": 15,
        "SP": 15,
        "DF": 10,
        "EP": 10
    }
}

# ENEMIES

enemies = {
    "Geargrub": {
        "HP": 40,
        "AK": 8,
        "SP": 6,
        "DF": 3,
        "EP": 5
    },
    "Scrapling": {
        "HP": 30,
        "AK": 10,
        "SP": 12,
        "DF": 2,
        "EP": 3
    }
}

# DIALOGUE

dialogues = {
    "3.00": "Welcome to the \"peaceful\" village of Chromehaven.",
    "3.01": "Hmm... Something seems off about this village.",
    "3.02": "Everyone here is acting strangely.",
    "3.03": "I should probably look around.",
    "3.04": "The village is strangely quiet.",
    "3.05": "There are people around...",
    "3.06": "... but nobody is talking.",
    "3.07": "Why is everyone looking at me?",
    "3.08": "I should probably find someone who can explain.",
    "3.09": "...a blacksmith, an inn, and a large town square...",
    "3.10": "...hopefully someone inside knows what's happening.",
    "3.11": "I guess there's only one way to find out."
}

speakers = {
    "3.00": "[Narrator]",
    "3.01": "[Knight]",
    "3.02": "[Knight]",
    "3.03": "[Knight]",
    "3.04": "[Knight]",
    "3.05": "[Knight]",
    "3.06": "[Knight]",
    "3.07": "[Knight]",
    "3.08": "[Knight]",
    "3.09": "[Knight]",
    "3.10": "[Knight]",
    "3.11": "[Knight]"
}

# GAME STATE

screen_stage = "1" if data.get("first_time", True) else "0"
selected_option = 0
previous_screen_stage = "0"
dlg_num = 0
running = True

cutscene_start_time = 0
cutscene_stage = 0

progress = 40
completed = progress // 20
remaining = 20 - completed

geargrub_defeated = data.get("geargrub_defeated", False)

# BATTLE STATE

battle_enemy = None
battle_enemy_stats = {}
battle_enemy_hp = 0
battle_player_hp = 0
battle_turn = "player"
battle_message = ""
battle_combo = 0
battle_crit = False
battle_defending = False

def start_battle(enemy_name):
    global battle_enemy
    global battle_enemy_stats
    global battle_enemy_hp
    global battle_player_hp
    global battle_turn
    global battle_message
    global battle_combo
    global battle_crit
    global battle_defending

    battle_enemy = enemy_name
    battle_enemy_stats = enemies[enemy_name].copy()
    battle_enemy_hp = battle_enemy_stats["HP"]
    battle_player_hp = player_stats["HP"]
    battle_turn = "player"
    battle_message = "A " + enemy_name + " appeared!"
    battle_combo = 0
    battle_crit = False
    battle_defending = False
    selected_option = 0

def finish_battle_victory():
    global geargrub_defeated
    global battle_turn
    global battle_message

    if battle_enemy == "Geargrub":
        geargrub_defeated = True
        data["geargrub_defeated"] = True
        save_game()

    battle_turn = "won"
    battle_message = "You defeated " + battle_enemy + "!"

# HOW IT WORKS

# battle_turn controls whose action is currently allowed:
# player = player chooses an action
# enemy = ENTER performs the enemy attack
# won = ENTER leaves the battle
# lost = ENTER returns to the game menu

# MUSIC

def update_music():
    global current_music

    if screen_stage in ["0", "1", "1001", "5"]:
        wanted_music = main_menu_music
    elif screen_stage.startswith("902"):
        wanted_music = settings_music
    elif screen_stage == "901":
        wanted_music = credits_music
    else:
        wanted_music = None

    if wanted_music != current_music:
        pygame.mixer.music.stop()

        if wanted_music:
            pygame.mixer.music.load(wanted_music)
            pygame.mixer.music.set_volume(0 if muted else 1)
            pygame.mixer.music.play(-1)

        current_music = wanted_music

# DRAW HELPERS

def draw_menu(options, x=900, y=600):
    for i, option in enumerate(options):
        prefix = "> " if i == selected_option else "  "

        if option in ["[Quit]", "{!WIPE SAVE!}", "[!Continue!]", "[!WIPE SAVE!]"]:
            colour = "red"
        elif i == selected_option:
            colour = "green"
        else:
            colour = "white"

        text = small_font.render(prefix + option, True, colour)
        screen.blit(text, (x, y + i * 60))

def draw_dialogue(speaker, text):
    pygame.draw.rect(screen, "black", (100, 850, 1400, 250))
    pygame.draw.rect(screen, "#3FA879", (100, 850, 1400, 250), 4)

    speaker_text = small_font.render(speaker, True, "#3FA879")
    dialogue_text = small_font.render(text, True, "#3FA879")
    continue_text = xsmall_font.render(
        "Press ENTER to continue",
        True,
        "purple"
    )

    screen.blit(speaker_text, (140, 875))
    screen.blit(dialogue_text, (200, 900))
    screen.blit(continue_text, (1150, 1050))

# HOW IT WORKS

# These small functions handle repeated drawing.
# This keeps the screen sections shorter without changing the game.

# MAIN LOOP

while running:
    can_pause = screen_stage not in [
        "0",
        "1",
        "00",
        "1001",
        "5",
        "6",
        "901",
        "902",
        "9021",
        "9022",
        "9025",
        "90252"
    ]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                continue

            if event.key == pygame.K_DELETE and can_pause:
                previous_screen_stage = screen_stage
                screen_stage = "00"
                selected_option = 0
                play_sound(pause_sound)
                continue

            # S0 MAIN MENU

            if screen_stage == "0":
                if event.key == pygame.K_UP:
                    selected_option -= 1
                    play_sound(menu_select_sound)

                elif event.key == pygame.K_DOWN:
                    selected_option += 1
                    play_sound(menu_select_sound)

                elif event.key == pygame.K_RETURN:
                    K_ent_sound()

                    if selected_option == 0:
                        screen_stage = "2"
                        selected_option = 0
                        play_sound(start_sound)

                    elif selected_option == 1:
                        screen_stage = "901"
                        selected_option = 0

                    elif selected_option == 2:
                        screen_stage = "902"
                        selected_option = 0

                    elif selected_option == 3:
                        running = False

                selected_option %= 4

            # S00 PAUSE

            elif screen_stage == "00":
                if event.key == pygame.K_UP:
                    selected_option -= 1
                    play_sound(menu_select_sound)

                elif event.key == pygame.K_DOWN:
                    selected_option += 1
                    play_sound(menu_select_sound)

                elif event.key == pygame.K_RETURN:
                    K_ent_sound()

                    if selected_option == 0:
                        screen_stage = previous_screen_stage
                        selected_option = 0

                    elif selected_option == 1:
                        screen_stage = "0"
                        selected_option = 0

                    elif selected_option == 2:
                        running = False

                selected_option %= 3

            # S1 NAME

            elif screen_stage == "1":
                if event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
                    play_sound(menu_select_sound)

                elif event.key == pygame.K_RETURN:
                    K_ent_sound()
                    data["name"] = name
                    save_game()
                    screen_stage = "1001"
                    selected_option = 0

                elif event.key == pygame.K_BACKSPACE:
                    K_bks_sound()
                    name = name[:-1]

                elif event.unicode.isprintable():
                    play_sound(menu_select_sound)
                    name += event.unicode

            # S1001 CONTROLS

            elif screen_stage == "1001":
                if event.key == pygame.K_RETURN:
                    K_ent_sound()
                    screen_stage = "5"
                    selected_option = 0

            # S2 GAME MENU

            elif screen_stage == "2":
                if event.key == pygame.K_UP:
                    selected_option -= 1
                    play_sound(menu_select_sound)

                elif event.key == pygame.K_DOWN:
                    selected_option += 1
                    play_sound(menu_select_sound)

                elif event.key == pygame.K_RETURN:
                    K_ent_sound()

                    if selected_option == 0:
                        if data.get("first_time", True):
                            if not data.get("opening_seen", False):
                                screen_stage = "6"
                                cutscene_start_time = pygame.time.get_ticks()
                                cutscene_stage = 0
                        else:
                            screen_stage = "3"
                            dlg_num = 0

                    elif selected_option == 1:
                        screen_stage = "4"

                elif event.key == pygame.K_INSERT:
                    screen_stage = "0"
                    selected_option = 0

                selected_option %= 2

            # S3 EXPLORE

            elif screen_stage == "3":
                if event.key == pygame.K_BACKSPACE:
                    K_bks_sound()
                    screen_stage = "2"
                    dlg_num = 0
                    selected_option = 0

                elif event.key == pygame.K_RETURN:
                    K_ent_sound()

                    if dlg_num < len(dialogues) - 1:
                        dlg_num += 1
                    elif not geargrub_defeated:
                        start_battle("Geargrub")
                        screen_stage = "7"
                        selected_option = 0
                    else:
                        screen_stage = "2"
                        selected_option = 0

            # S4 TRAIN

            elif screen_stage == "4":
                if event.key == pygame.K_BACKSPACE:
                    K_bks_sound()
                    screen_stage = "2"
                    selected_option = 0

            # S5 CLASS SELECTION

            elif screen_stage == "5":
                if event.key == pygame.K_UP:
                    selected_option -= 1
                    play_sound(menu_select_sound)

                elif event.key == pygame.K_DOWN:
                    selected_option += 1
                    play_sound(menu_select_sound)

                elif event.key == pygame.K_RETURN:
                    K_ent_sound()

                    class_names = list(classes.keys())
                    player_class = class_names[selected_option]
                    player_stats = classes[player_class].copy()

                    data["class"] = player_class
                    data["level"] = 1
                    data["EXP"] = 0

                    for stat in player_stats:
                        data[stat] = player_stats[stat]

                    save_game()

                    screen_stage = "6"
                    cutscene_start_time = pygame.time.get_ticks()
                    cutscene_stage = 0
                    selected_option = 0

                selected_option %= len(classes)

            # S6 OPENING CUTSCENE

            elif screen_stage == "6":
                if event.key == pygame.K_RETURN:
                    K_ent_sound()

                    if cutscene_stage >= 5:
                        data["opening_seen"] = True
                        data["first_time"] = False
                        save_game()
                        screen_stage = "2"
                        selected_option = 0

            # S7 BATTLE

            elif screen_stage == "7":
                if battle_turn == "player":
                    if event.key == pygame.K_UP:
                        selected_option -= 1
                        play_sound(menu_select_sound)

                    elif event.key == pygame.K_DOWN:
                        selected_option += 1
                        play_sound(menu_select_sound)

                    elif event.key == pygame.K_RETURN:
                        K_ent_sound()

                        if selected_option == 0:
                            base_damage = max(
                                1,
                                player_stats["AK"] - battle_enemy_stats["DF"]
                            )

                            critical = random.random() < 0.15
                            combo_multiplier = 1 + battle_combo * 0.10
                            damage = int(base_damage * combo_multiplier)

                            if critical:
                                damage = int(damage * 1.75)
                                battle_crit = True
                            else:
                                battle_crit = False

                            battle_enemy_hp -= damage
                            battle_combo += 1

                            if critical:
                                battle_message = (
                                    "CRITICAL HIT! "
                                    + str(damage)
                                    + " DAMAGE!"
                                )
                            elif battle_combo >= 2:
                                battle_message = (
                                    str(battle_combo)
                                    + " HIT COMBO! "
                                    + str(damage)
                                    + " DAMAGE!"
                                )
                            else:
                                battle_message = (
                                    "You dealt "
                                    + str(damage)
                                    + " damage!"
                                )

                            if battle_enemy_hp <= 0:
                                battle_enemy_hp = 0
                                finish_battle_victory()
                            else:
                                battle_turn = "enemy"

                        elif selected_option == 1:
                            battle_defending = True
                            battle_message = "You defended!"
                            battle_turn = "enemy"

                        elif selected_option == 2:
                            battle_message = "You have no items yet!"

                        elif selected_option == 3:
                            battle_message = "You escaped!"
                            screen_stage = "3"
                            selected_option = 0

                    selected_option %= 4

                elif battle_turn == "enemy":
                    if event.key == pygame.K_RETURN:
                        K_ent_sound()

                        damage = max(
                            1,
                            battle_enemy_stats["AK"] - player_stats["DF"]
                        )

                        if battle_defending:
                            damage = max(1, damage // 2)
                            battle_defending = False

                        battle_player_hp -= damage

                        battle_message = (
                            battle_enemy
                            + " dealt "
                            + str(damage)
                            + " damage!"
                        )

                        if battle_player_hp <= 0:
                            battle_player_hp = 0
                            battle_turn = "lost"
                            battle_message = "You were defeated!"
                        else:
                            battle_turn = "player"
                            battle_crit = False
                            selected_option = 0

                elif battle_turn == "won":
                    if event.key == pygame.K_RETURN:
                        K_ent_sound()
                        screen_stage = "3"
                        selected_option = 0
                        dlg_num = len(dialogues) - 1

                elif battle_turn == "lost":
                    if event.key == pygame.K_RETURN:
                        K_ent_sound()
                        screen_stage = "2"
                        selected_option = 0
                        battle_player_hp = player_stats["HP"]

            # S901 CREDITS

            elif screen_stage == "901":
                if event.key == pygame.K_BACKSPACE:
                    K_bks_sound()
                    selected_option = 1
                    screen_stage = "0"

            # S902 SETTINGS

            elif screen_stage == "902":
                if event.key == pygame.K_UP:
                    selected_option -= 1
                    play_sound(menu_select_sound)

                elif event.key == pygame.K_DOWN:
                    selected_option += 1
                    play_sound(menu_select_sound)

                elif event.key == pygame.K_BACKSPACE:
                    K_bks_sound()
                    selected_option = 2
                    screen_stage = "0"

                elif event.key == pygame.K_RETURN:
                    K_ent_sound()

                    if selected_option == 0:
                        print("General settings undefined")

                    elif selected_option == 1:
                        selected_option = 0
                        screen_stage = "9022"

                    elif selected_option == 2:
                        print("Video settings undefined")

                    elif selected_option == 3:
                        selected_option = 0
                        screen_stage = "9021"

                    elif selected_option == 4:
                        selected_option = 0
                        screen_stage = "9025"

                selected_option %= 5

            # S9022 AUDIO

            elif screen_stage == "9022":
                if event.key == pygame.K_UP:
                    selected_option -= 1
                    play_sound(menu_select_sound)

                elif event.key == pygame.K_DOWN:
                    selected_option += 1
                    play_sound(menu_select_sound)

                elif event.key == pygame.K_BACKSPACE:
                    K_bks_sound()
                    selected_option = 1
                    screen_stage = "902"

                elif event.key == pygame.K_RETURN:
                    K_ent_sound()

                    if selected_option == 0:
                        muted = not muted
                        update_mute()

                    elif selected_option == 1:
                        selected_option = 1
                        screen_stage = "902"

                selected_option %= 2

            # S9021 ADVANCED

            elif screen_stage == "9021":
                if event.key == pygame.K_BACKSPACE:
                    K_bks_sound()
                    selected_option = 3
                    screen_stage = "902"

            # S9025 WIPE WARNING

            elif screen_stage == "9025":
                if event.key == pygame.K_UP:
                    selected_option -= 1
                    play_sound(menu_select_sound)

                elif event.key == pygame.K_DOWN:
                    selected_option += 1
                    play_sound(menu_select_sound)

                elif event.key == pygame.K_BACKSPACE:
                    K_bks_sound()
                    selected_option = 4
                    screen_stage = "902"

                elif event.key == pygame.K_RETURN:
                    K_ent_sound()

                    if selected_option == 0:
                        selected_option = 4
                        screen_stage = "902"

                    elif selected_option == 1:
                        selected_option = 0
                        screen_stage = "90252"

                selected_option %= 2

            # S90252 FINAL WIPE

            elif screen_stage == "90252":
                if event.key == pygame.K_UP:
                    selected_option -= 1
                    play_sound(menu_select_sound)

                elif event.key == pygame.K_DOWN:
                    selected_option += 1
                    play_sound(menu_select_sound)

                elif event.key == pygame.K_BACKSPACE:
                    K_bks_sound()
                    selected_option = 4
                    screen_stage = "902"

                elif event.key == pygame.K_RETURN:
                    K_ent_sound()

                    if selected_option == 0:
                        selected_option = 4
                        screen_stage = "902"

                    elif selected_option == 1:
                        reset_save()
                        selected_option = 0
                        screen_stage = "1"

                selected_option %= 2

    # MUSIC

    update_music()
    screen.fill("black")

    # S0 MAIN MENU

    if screen_stage == "0":
        title_lines = [
            "██╗  ██╗███╗   ██╗██╗ ██████╗ ██╗  ██╗████████╗",
            "██║ ██╔╝████╗  ██║██║██╔════╝ ██║  ██║╚══██╔══╝",
            "█████╔╝ ██╔██╗ ██║██║██║  ███╗███████║   ██║",
            "██╔═██╗ ██║╚██╗██║██║██║   ██║██╔══██║   ██║",
            "██║  ██╗██║ ╚████║██║╚██████╔╝██║  ██║   ██║",
            "╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝",
            "██████╗ ██╗   ██╗████████╗███████╗",
            "██╔══██╗╚██╗ ██╔╝╚══██╔══╝██╔════╝",
            "██████╔╝ ╚████╔╝    ██║   █████╗",
            "██╔══██╗  ╚██╔╝     ██║   ██╔══╝",
            "██████╔╝   ██║      ██║   ███████╗",
            "╚═════╝    ╚═╝      ╚═╝   ╚══════╝",
            "Knight Simulator v0.8"
        ]

        y = 300
        for line in title_lines:
            screen.blit(
                xsmall_font.render(line, True, "white"),
                (100, y)
            )
            y += 15

        screen.blit(
            small_font.render("//By IntelI9 and K_muistaa501", True, "white"),
            (100, 600)
        )
        screen.blit(
            small_font.render("//Made for Project Stardance 2026", True, "white"),
            (100, 640)
        )
        screen.blit(
            normal_font.render(
                "Press Esc to quit at any time",
                True,
                "purple"
            ),
            (100, 950)
        )

        if not data.get("first_time", True):
            screen.blit(
                small_font.render(
                    "Welcome, Knight " + name + "!",
                    True,
                    "white"
                ),
                (100, 700)
            )

        progress_bar = "[" + "¦" * completed + "█" * remaining + "]"

        screen.blit(
            small_font.render(progress_bar, True, "dark green"),
            (100, 750)
        )
        screen.blit(
            normal_font.render(
                f"{completed * 20}% completed [Chapter: {screen_stage}]",
                True,
                "white"
            ),
            (100, 800)
        )

        draw_menu(
            ["[Start]", "[Credits]", "[Settings]", "[Quit]"]
        )

    # S00 PAUSE

    elif screen_stage == "00":
        draw_menu(
            ["[Back]", "[To Start Menu]", "[Quit]"]
        )

    # S1 NAME

    elif screen_stage == "1":
        screen.blit(
            small_font.render(
                "Type your knight's name:",
                True,
                "white"
            ),
            (220, 330)
        )

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            cursor = "^"
        elif pygame.time.get_ticks() % 500 < 250:
            cursor = "|"
        else:
            cursor = ""

        screen.blit(
            normal_font.render(
                name + cursor,
                True,
                "green"
            ),
            (220, 380)
        )

        press_text = small_font.render("Press ", True, "white")
        enter_text = small_font.render("ENTER", True, "purple")
        continue_text = small_font.render(" to continue", True, "white")

        x = 210
        screen.blit(press_text, (x, 440))
        x += press_text.get_width()
        screen.blit(enter_text, (x, 440))
        x += enter_text.get_width()
        screen.blit(continue_text, (x, 440))

    # S2 GAME MENU

    elif screen_stage == "2":
        screen.blit(
            normal_font.render(
                "Welcome, Knight " + name + "!",
                True,
                "white"
            ),
            (220, 300)
        )

        draw_menu(["[Explore]", "[Train]"])

    # S3 EXPLORE

    elif screen_stage == "3":
        village = pygame.image.load(
            "images/Old Village 2.jpg"
        ).convert()

        village = pygame.transform.scale(
            village,
            (1600, 1200)
        )

        screen.blit(village, (0, 0))

        dialogue_id = f"{screen_stage}.{dlg_num:02d}"

        draw_dialogue(
            speakers.get(dialogue_id, ""),
            dialogues.get(dialogue_id, "")
        )

    # S4 TRAIN

    elif screen_stage == "4":
        screen.blit(
            small_font.render(
                'Welcome to the "peaceful" village of Chromehaven.',
                True,
                "white"
            ),
            (200, 400)
        )

        draw_dialogue(
            "Knight",
            "Training will be added soon."
        )

    # S5 CLASS SELECTION

    elif screen_stage == "5":
        screen.blit(
            normal_font.render(
                name + ", choose your Knight Class",
                True,
                "white"
            ),
            (200, 180)
        )

        class_names = list(classes.keys())
        preview_class = class_names[selected_option]
        preview_stats = classes[preview_class]

        options = [
            "[Soldier]",
            "[Assassin]",
            "[Barbarian]",
            "[Archer]",
            "[Guardian]",
            "[Duelist]"
        ]

        draw_menu(options, 250, 350)

        screen.blit(
            small_font.render(
                preview_class + " Stats",
                True,
                "#3FA879"
            ),
            (900, 350)
        )

        for i, stat in enumerate(["HP", "AK", "SP", "DF", "EP"]):
            screen.blit(
                small_font.render(
                    f"{stat}: {preview_stats[stat]}",
                    True,
                    "white"
                ),
                (900, 420 + i * 55)
            )

        screen.blit(
            small_font.render(
                "Press ENTER to select",
                True,
                "purple"
            ),
            (900, 750)
        )
        screen.blit(
            small_font.render(
                "You cannot change this after!",
                True,
                "#C81A1A"
            ),
            (900, 850)
        )

    # S6 OPENING CUTSCENE

    elif screen_stage == "6":
        elapsed = (
            pygame.time.get_ticks() - cutscene_start_time
        ) / 1000

        if elapsed < 3:
            cutscene_stage = 0
        elif elapsed < 6:
            cutscene_stage = 1
        elif elapsed < 9:
            cutscene_stage = 2
        elif elapsed < 12:
            cutscene_stage = 3
        elif elapsed < 16:
            cutscene_stage = 4
        else:
            cutscene_stage = 5

        cutscene_text = [
            "You were just coding...",
            "..until you opened a file...",
            "...that pulled you into your screen.",
            "The brightness of the room leaves.",
            "Welcome, Knight " + name + "."
        ]

        if cutscene_stage < 5:
            screen.blit(
                normal_font.render(
                    cutscene_text[cutscene_stage],
                    True,
                    "white"
                ),
                (400, 450)
            )
        else:
            screen.blit(
                big_font.render(
                    "To Chromehaven.",
                    True,
                    "blue"
                ),
                (450, 450)
            )
            screen.blit(
                small_font.render(
                    "Press ENTER to continue",
                    True,
                    "purple"
                ),
                (450, 650)
            )

    # S1001 CONTROLS

    elif screen_stage == "1001":
        screen.blit(
            normal_font.render(
                "Use [UP] and [DOWN] arrows to navigate menus",
                True,
                "purple"
            ),
            (100, 350)
        )
        screen.blit(
            normal_font.render(
                "[Enter] (Return) to select/continue (press now!)",
                True,
                "white"
            ),
            (100, 450)
        )
        screen.blit(
            normal_font.render(
                "[Backspace] to go back",
                True,
                "purple"
            ),
            (100, 550)
        )
        screen.blit(
            normal_font.render(
                "Enjoy the game!",
                True,
                "blue"
            ),
            (100, 650)
        )

    # S7 BATTLE

    elif screen_stage == "7":
        screen.blit(
            normal_font.render(
                "BATTLE!",
                True,
                "red"
            ),
            (200, 150)
        )

        screen.blit(
            normal_font.render(
                battle_enemy,
                True,
                "white"
            ),
            (1000, 300)
        )

        screen.blit(
            small_font.render(
                f"HP: {battle_enemy_hp}/{battle_enemy_stats['HP']}",
                True,
                "red"
            ),
            (1000, 370)
        )

        screen.blit(
            normal_font.render(
                name,
                True,
                "white"
            ),
            (200, 650)
        )

        screen.blit(
            small_font.render(
                f"HP: {battle_player_hp}/{player_stats['HP']}",
                True,
                "green"
            ),
            (200, 720)
        )

        if battle_combo >= 2:
            screen.blit(
                small_font.render(
                    "COMBO x" + str(battle_combo),
                    True,
                    "yellow"
                ),
                (200, 800)
            )

        if battle_crit:
            screen.blit(
                small_font.render(
                    "CRITICAL!",
                    True,
                    "red"
                ),
                (200, 750)
            )

        screen.blit(
            small_font.render(
                battle_message,
                True,
                "white"
            ),
            (200, 850)
        )

        # HOW IT WORKS
        # The battle menu is only visible during the player's turn.
        # This stops Attack/Defend/Item/Run appearing while the enemy,
        # victory or defeat state is active.

        if battle_turn == "player":
            draw_menu(
                ["[Attack]", "[Defend]", "[Item]", "[Run]"],
                1000,
                600
            )

        elif battle_turn == "enemy":
            screen.blit(
                xsmall_font.render(
                    "Press ENTER for the enemy's turn",
                    True,
                    "purple"
                ),
                (1000, 900)
            )

        elif battle_turn == "won":
            screen.blit(
                xsmall_font.render(
                    "Press ENTER to continue",
                    True,
                    "purple"
                ),
                (1000, 900)
            )

        elif battle_turn == "lost":
            screen.blit(
                xsmall_font.render(
                    "Press ENTER to continue",
                    True,
                    "purple"
                ),
                (1000, 900)
            )

    # S901 CREDITS

    elif screen_stage == "901":
        screen.blit(
            normal_font.render(
                "//KnightByte by K_muistaa501 & IntelI9 (C) 2026",
                True,
                "#00E5FF"
            ),
            (100, 200)
        )
        screen.blit(
            small_font.render(
                "//Ascii by patryojk on",
                True,
                "purple"
            ),
            (100, 250)
        )
        screen.blit(
            small_font.render(
                "https://patorjk.com/software/taag/",
                True,
                "green"
            ),
            (100, 300)
        )
        screen.blit(
            small_font.render(
                "//This code was partially generated by ChatGPT",
                True,
                "purple"
            ),
            (100, 350)
        )
        screen.blit(
            small_font.render(
                "Thanks Hack Club!!! We wouldn't code if it weren't for you",
                True,
                "blue"
            ),
            (100, 400)
        )
        screen.blit(
            small_font.render(
                "Press BACKSPACE to go back",
                True,
                "purple"
            ),
            (200, 900)
        )

    # S902 SETTINGS

    elif screen_stage == "902":
        screen.blit(
            small_font.render(
                "Settings",
                True,
                "white"
            ),
            (200, 400)
        )
        screen.blit(
            small_font.render(
                "Press BACKSPACE to go back",
                True,
                "purple"
            ),
            (200, 450)
        )

        draw_menu(
            [
                "[General]",
                "[Audio]",
                "[Video]",
                "[Advanced FOR NERDS ONLY]",
                "{!WIPE SAVE!}"
            ]
        )

    # S9022 AUDIO

    elif screen_stage == "9022":
        screen.blit(
            small_font.render(
                "Audio Settings",
                True,
                "white"
            ),
            (200, 400)
        )
        screen.blit(
            small_font.render(
                "Press BACKSPACE to go back",
                True,
                "purple"
            ),
            (200, 500)
        )

        mute_status = "ON" if muted else "OFF"

        draw_menu(
            [
                "[Mute: " + mute_status + "]",
                "[Back]"
            ]
        )

    # S9021 ADVANCED

    elif screen_stage == "9021":
        screen.blit(
            small_font.render(
                "This will be peak! Advanced settings coming soon!",
                True,
                "orange"
            ),
            (200, 400)
        )
        screen.blit(
            small_font.render(
                "Press BACKSPACE to go back",
                True,
                "purple"
            ),
            (200, 500)
        )

    # S9025 WIPE WARNING

    elif screen_stage == "9025":
        screen.blit(
            small_font.render(
                "WARNING!",
                True,
                "red"
            ),
            (200, 300)
        )
        screen.blit(
            small_font.render(
                "This will delete your save data.",
                True,
                "yellow"
            ),
            (200, 370)
        )
        screen.blit(
            small_font.render(
                "Your knight's name will be lost to the 404 grave of abyss.",
                True,
                "red"
            ),
            (200, 420)
        )

        draw_menu(
            ["[Cancel]", "[!Continue!]"]
        )

    # S90252 FINAL WIPE

    elif screen_stage == "90252":
        screen.blit(
            small_font.render(
                "WARNING!",
                True,
                "red"
            ),
            (200, 300)
        )
        screen.blit(
            small_font.render(
                "This will delete your save data.",
                True,
                "yellow"
            ),
            (200, 370)
        )
        screen.blit(
            small_font.render(
                "Your knight's name will be lost to the 404 grave of abyss.",
                True,
                "red"
            ),
            (200, 420)
        )
        screen.blit(
            small_font.render(
                "ARE YOU SURE YOU WANT TO DELETE YOUR DATA",
                True,
                "purple"
            ),
            (200, 470)
        )

        draw_menu(
            ["[Cancel]", "[!WIPE SAVE!]"]
        )

    pygame.display.flip()
    clock.tick(60)

# CLEANUP

pygame.quit()
```
