#!/usr/bin/env python3
"""
Convert ZMK Keymap (config/zitaotech_keypoint.keymap) to ZitaoTech Studio / KeyboardHub Abyss JSON format.
Preserves existing hardware settings (trackpoint, trackpad, layout positions) while updating layers,
encoders, and combos from the native .keymap file.
"""

import os
import re
import sys
import json
import datetime
import shutil

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYMAP_FILE = os.path.join(REPO_ROOT, "config", "zitaotech_keypoint.keymap")
JSON_FILE = os.path.join(REPO_ROOT, "KEYPOINT-keymap-2026-10-25.json")
BACKUP_FILE = os.path.join(REPO_ROOT, "KEYPOINT-keymap-2026-10-25.original.json")

KP_MAP = {
    # Letters
    "A": (4, "keyboard", []), "B": (5, "keyboard", []), "C": (6, "keyboard", []), "D": (7, "keyboard", []),
    "E": (8, "keyboard", []), "F": (9, "keyboard", []), "G": (10, "keyboard", []), "H": (11, "keyboard", []),
    "I": (12, "keyboard", []), "J": (13, "keyboard", []), "K": (14, "keyboard", []), "L": (15, "keyboard", []),
    "M": (16, "keyboard", []), "N": (17, "keyboard", []), "O": (18, "keyboard", []), "P": (19, "keyboard", []),
    "Q": (20, "keyboard", []), "R": (21, "keyboard", []), "S": (22, "keyboard", []), "T": (23, "keyboard", []),
    "U": (24, "keyboard", []), "V": (25, "keyboard", []), "W": (26, "keyboard", []), "X": (27, "keyboard", []),
    "Y": (28, "keyboard", []), "Z": (29, "keyboard", []),
    # Numbers
    "N1": (30, "keyboard", []), "N2": (31, "keyboard", []), "N3": (32, "keyboard", []), "N4": (33, "keyboard", []),
    "N5": (34, "keyboard", []), "N6": (35, "keyboard", []), "N7": (36, "keyboard", []), "N8": (37, "keyboard", []),
    "N9": (38, "keyboard", []), "N0": (39, "keyboard", []),
    # Controls / Editing
    "ENTER": (40, "keyboard", []), "ESC": (41, "keyboard", []), "BSPC": (42, "keyboard", []), "TAB": (43, "keyboard", []),
    "SPACE": (44, "keyboard", []), "MINUS": (45, "keyboard", []), "EQUAL": (46, "keyboard", []),
    "LBKT": (47, "keyboard", []), "LEFT_BRACKET": (47, "keyboard", []),
    "RBKT": (48, "keyboard", []), "RIGHT_BRACKET": (48, "keyboard", []),
    "BSLH": (49, "keyboard", []), "BACKSLASH": (49, "keyboard", []),
    "SEMI": (51, "keyboard", []), "SEMICOLON": (51, "keyboard", []),
    "SQT": (52, "keyboard", []), "SINGLE_QUOTE": (52, "keyboard", []),
    "GRAVE": (53, "keyboard", []), "COMMA": (54, "keyboard", []), "DOT": (55, "keyboard", []),
    "FSLH": (56, "keyboard", []), "SLASH": (56, "keyboard", []),
    "CAPS": (57, "keyboard", []),
    # Function Keys
    "F1": (58, "keyboard", []), "F2": (59, "keyboard", []), "F3": (60, "keyboard", []), "F4": (61, "keyboard", []),
    "F5": (62, "keyboard", []), "F6": (63, "keyboard", []), "F7": (64, "keyboard", []), "F8": (65, "keyboard", []),
    "F9": (66, "keyboard", []), "F10": (67, "keyboard", []), "F11": (68, "keyboard", []), "F12": (69, "keyboard", []),
    # Navigation / System
    "PRINTSCREEN": (70, "keyboard", []), "SCROLLLOCK": (71, "keyboard", []), "PAUSE_BREAK": (72, "keyboard", []),
    "INSERT": (73, "keyboard", []), "HOME": (74, "keyboard", []), "PAGE_UP": (75, "keyboard", []), "PG_UP": (75, "keyboard", []),
    "DEL": (76, "keyboard", []), "END": (77, "keyboard", []), "PAGE_DOWN": (78, "keyboard", []), "PG_DN": (78, "keyboard", []),
    "RIGHT": (79, "keyboard", []), "RIGHT_ARROW": (79, "keyboard", []), "LEFT_ARROW": (80, "keyboard", []),
    "DOWN_ARROW": (81, "keyboard", []), "UP_ARROW": (82, "keyboard", []),
    # Modifiers
    "LCTRL": (224, "keyboard", []), "LEFT_CONTROL": (224, "keyboard", []),
    "LSHFT": (225, "keyboard", []), "LALT": (226, "keyboard", []), "LGUI": (227, "keyboard", []),
    "RCTRL": (228, "keyboard", []), "RIGHT_CONTROL": (228, "keyboard", []),
    "RSHFT": (229, "keyboard", []), "RIGHT_SHIFT": (229, "keyboard", []),
    "RALT": (230, "keyboard", []), "RIGHT_ALT": (230, "keyboard", []),
    "RGUI": (231, "keyboard", []), "RIGHT_GUI": (231, "keyboard", []),
    # Consumer
    "C_MUTE": (226, "consumer", []), "C_PLAY": (205, "consumer", []), "C_POWER": (48, "consumer", []),
    # Shifted Symbols
    "EXCL": (30, "keyboard", ["LSHIFT"]), "AT_SIGN": (31, "keyboard", ["LSHIFT"]), "HASH": (32, "keyboard", ["LSHIFT"]),
    "DOLLAR": (33, "keyboard", ["LSHIFT"]), "PERCENT": (34, "keyboard", ["LSHIFT"]), "CARET": (35, "keyboard", ["LSHIFT"]),
    "AMPERSAND": (36, "keyboard", ["LSHIFT"]), "ASTERISK": (37, "keyboard", ["LSHIFT"]),
    "LEFT_PARENTHESIS": (38, "keyboard", ["LSHIFT"]), "RIGHT_PARENTHESIS": (39, "keyboard", ["LSHIFT"]),
    "UNDERSCORE": (45, "keyboard", ["LSHIFT"]), "PLUS": (46, "keyboard", ["LSHIFT"]),
    "LEFT_BRACE": (47, "keyboard", ["LSHIFT"]), "RIGHT_BRACE": (48, "keyboard", ["LSHIFT"]),
    "PIPE": (49, "keyboard", ["LSHIFT"]), "COLON": (51, "keyboard", ["LSHIFT"]),
    "TILDE": (53, "keyboard", ["LSHIFT"]), "QUESTION": (56, "keyboard", ["LSHIFT"]),
    # Mod-Keys
    "LC(DOWN_ARROW)": (81, "keyboard", ["LCTRL"]), "LC(UP_ARROW)": (82, "keyboard", ["LCTRL"]),
    "LG(N1)": (30, "keyboard", ["LGUI"]), "LG(N2)": (31, "keyboard", ["LGUI"]), "LG(N3)": (32, "keyboard", ["LGUI"]),
    "LG(N4)": (33, "keyboard", ["LGUI"]), "LG(N5)": (34, "keyboard", ["LGUI"]), "LG(N6)": (35, "keyboard", ["LGUI"]),
    "LG(N7)": (36, "keyboard", ["LGUI"]), "LG(N8)": (37, "keyboard", ["LGUI"]), "LG(N9)": (38, "keyboard", ["LGUI"]),
    "LG(N0)": (39, "keyboard", ["LGUI"]),
}

LAYER_META = [
    ("default_layer", "QWERTY"),
    ("ORANGE_layer", "ORANGE"),
    ("MOUSE_layer", "MOUSE"),
    ("NAVIG_layer", "NAVIGATION"),
    ("SYMBOL_layer", "SYMBOL"),
    ("NUMBER_layer", "NUMBER"),
    ("FUNCTION_layer", "FUNCTION"),
]

def map_binding(b):
    if b == "&trans":
        return {"type": "trans"}
    if b == "&none":
        return {"type": "none"}
    if b in ("&bootloader", "&BOT"):
        return {"type": "bootloader"}
    if b == "&bt BT_CLR":
        return {"type": "bluetooth", "action": "clear"}
    if b == "&out OUT_TOG":
        return {"type": "output", "action": "toggle"}
    if b == "&to MOUSE":
        return {"type": "to", "layer": 2}
    if b == "&mo ORANGE":
        return {"type": "mo", "layer": 1}
    if b == "&mo NAVIG":
        return {"type": "mo", "layer": 3}
    if b == "&mo SYMBOL":
        return {"type": "mo", "layer": 4}
    if b == "&mo NUMBER":
        return {"type": "mo", "layer": 5}
    if b == "&mo FUNCTION":
        return {"type": "mo", "layer": 6}
    if b in ("&mkp LCLK", "&mkp MB1"):
        return {"type": "mouse_button", "button": 1}
    if b in ("&mkp RCLK", "&mkp MB2"):
        return {"type": "mouse_button", "button": 2}
    if b in ("&mkp MCLK", "&mkp MB3"):
        return {"type": "mouse_button", "button": 3}
    if b == "&msc SCRL_DOWN":
        return {"type": "mouse_scroll", "direction": "down", "speed": 10}
    if b == "&msc SCRL_UP":
        return {"type": "mouse_scroll", "direction": "up", "speed": 10}
    
    # Custom behaviors
    if b.startswith("&hm "):
        return {"type": "raw", "zmk": b, "label": b.replace("&hm ", "HM ")}
    if b.startswith("&arrow_ht "):
        return {"type": "raw", "zmk": b, "label": b.replace("&arrow_ht 0 ", "Arrow HT ")}
    if b == "&mt LGUI ESC":
        return {"type": "raw", "zmk": "&mt LGUI ESC", "label": "Mod-Tap Gui Esc"}
    if b == "&lt_c NAVIG SPACE":
        return {"type": "raw", "zmk": "&lt_c 3 SPACE", "label": "LT Navig Space"}
    if b == "&lt_lower_enter ORANGE ENTER":
        return {"type": "raw", "zmk": "&lt_lower_enter 1 ENTER", "label": "LT Orange Enter"}
    if b == "&lt_c NUMBER SPACE":
        return {"type": "raw", "zmk": "&lt_c 5 SPACE", "label": "LT Number Space"}
    if b == "&M_kp MB1 J":
        return {"type": "raw", "zmk": "&M_kp MB1 J", "label": "Mouse KP J"}
    if b == "&tdLMCLK":
        return {"type": "raw", "zmk": "&tdLMCLK", "label": "TD LMCLK"}
    if b == "&tdRMCLK":
        return {"type": "raw", "zmk": "&tdRMCLK", "label": "TD RMCLK"}
    if b == "&LMouse_sc 0 MB1":
        return {"type": "raw", "zmk": "&LMouse_sc 0 MB1", "label": "LMouse Scroll"}
    if b in ("&bl BL_DEC", "&bl BL_INC"):
        return {"type": "raw", "zmk": b, "label": "Backlight " + ("Dec" if "DEC" in b else "Inc")}

    # Standard keys
    if b.startswith("&kp "):
        code = b[4:].strip()
        if code in KP_MAP:
            usage, upage, mods = KP_MAP[code]
            res = {"type": "key", "usage": usage, "usagePage": upage}
            if mods:
                res["mods"] = mods
            return res
        return {"type": "raw", "zmk": b, "label": code}
    
    return {"type": "raw", "zmk": b}

def main():
    print(f"Reading keymap from: {KEYMAP_FILE}")
    with open(KEYMAP_FILE, "r") as f:
        text = f.read()

    # Backup original JSON if backup does not already exist
    if os.path.exists(JSON_FILE) and not os.path.exists(BACKUP_FILE):
        print(f"Creating backup of original export at: {BACKUP_FILE}")
        shutil.copyfile(JSON_FILE, BACKUP_FILE)

    # Load template
    template_src = BACKUP_FILE if os.path.exists(BACKUP_FILE) else JSON_FILE
    with open(template_src, "r") as f:
        data = json.load(f)

    # Clean comments from keymap text
    text_clean = re.sub(r"/\*.*?\*/", "", text)
    text_clean = re.sub(r"//.*", "", text_clean)

    # Parse combos with brace counting
    start_combos = text_clean.find("combos {")
    combos_list = []
    if start_combos != -1:
        depth = 0
        combos_body = ""
        for i in range(start_combos, len(text_clean)):
            if text_clean[i] == "{":
                depth += 1
            elif text_clean[i] == "}":
                depth -= 1
                if depth == 0:
                    combos_body = text_clean[start_combos:i+1]
                    break
        combo_blocks = re.findall(r"(\w+)\s*\{([^\{\}]*)\}", combos_body)
        for cname, cbody in combo_blocks:
            kp_match = re.search(r"key-positions\s*=\s*<([^>]+)>;", cbody)
            b_match = re.search(r"bindings\s*=\s*<([^>]+)>;", cbody)
            if kp_match and b_match:
                pos = sorted([int(x) for x in kp_match.group(1).split()])
                b_str = b_match.group(1).strip()
                combos_list.append({
                    "positions": pos,
                    "binding": map_binding(b_str)
                })

    # Parse layers
    start_km = text_clean.find("keymap {")
    end_km = text_clean.rfind("};")
    km_content = text_clean[start_km:end_km]
    layers_raw = dict(re.findall(r"(\w+)\s*\{([^\{\}]*bindings\s*=\s*<[^>]+>[^\{\}]*)\}", km_content))

    new_layers = []
    for lkey, ldisplay in LAYER_META:
        if lkey not in layers_raw:
            print(f"Warning: layer {lkey} not found in keymap!")
            continue
        body = layers_raw[lkey]
        b_match = re.search(r"bindings\s*=\s*<([^>]+)>", body)
        bindings = re.findall(r"&[a-zA-Z0-9_]+(?:\s+[a-zA-Z0-9_\(\)]+)*", b_match.group(1))
        
        layer_obj = {
            "name": ldisplay,
            "bindings": [map_binding(b) for b in bindings]
        }

        # Add encoder bindings for Layer 0 (QWERTY) and Layer 1 (ORANGE)
        if ldisplay == "QWERTY":
            layer_obj["modules"] = [
                {
                    "name": "encoder_left",
                    "type": "rotary_encoder",
                    "clockwise": {"type": "key", "usage": 233, "usagePage": "consumer"},
                    "counterClockwise": {"type": "key", "usage": 234, "usagePage": "consumer"},
                    "firmwareDialect": {
                        "zmk": {
                            "cormoran_rsr": {
                                "sensorIndex": 0,
                                "clockwiseTapMs": 5,
                                "counterClockwiseTapMs": 5
                            }
                        }
                    }
                },
                {
                    "name": "encoder_right",
                    "type": "rotary_encoder",
                    "clockwise": {"type": "key", "usage": 182, "usagePage": "consumer"},
                    "counterClockwise": {"type": "key", "usage": 181, "usagePage": "consumer"},
                    "firmwareDialect": {
                        "zmk": {
                            "cormoran_rsr": {
                                "sensorIndex": 1,
                                "clockwiseTapMs": 5,
                                "counterClockwiseTapMs": 5
                            }
                        }
                    }
                }
            ]
        elif ldisplay == "ORANGE":
            layer_obj["modules"] = [
                {
                    "name": "encoder_left",
                    "type": "rotary_encoder",
                    "clockwise": {"type": "bluetooth", "action": "next"},
                    "counterClockwise": {"type": "bluetooth", "action": "previous"},
                    "firmwareDialect": {
                        "zmk": {
                            "cormoran_rsr": {
                                "sensorIndex": 0,
                                "clockwiseTapMs": 5,
                                "counterClockwiseTapMs": 5
                            }
                        }
                    }
                },
                {
                    "name": "encoder_right",
                    "type": "rotary_encoder",
                    "clockwise": {"type": "key", "usage": 82, "usagePage": "keyboard"},
                    "counterClockwise": {"type": "key", "usage": 81, "usagePage": "keyboard"},
                    "firmwareDialect": {
                        "zmk": {
                            "cormoran_rsr": {
                                "sensorIndex": 1,
                                "clockwiseTapMs": 5,
                                "counterClockwiseTapMs": 5
                            }
                        }
                    }
                }
            ]
        new_layers.append(layer_obj)

    # Update exportedAt
    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    data["exportedAt"] = now_iso

    # Update keymap structure
    data["keymap"]["name"] = "KEYPOINT Config Keymap"
    data["keymap"]["description"] = "Generated from zitaotech_keypoint.keymap"
    data["keymap"]["layers"] = new_layers
    data["keymap"]["combos"] = combos_list

    # Ensure sections declare combos
    data["sections"]["combos"] = True

    # Write output to KEYPOINT-keymap-2026-10-25.json
    print(f"Writing mapped JSON to: {JSON_FILE}")
    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    print(f"Successfully mapped {len(new_layers)} layers and {len(combos_list)} combos.")

if __name__ == "__main__":
    main()
