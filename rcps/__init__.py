
rcps = {
    "Boiler": {
        "req": [
            ("COAL", 1),
            ("WATER", 10)
        ],
        "mak": [
            ("STEAM", 100)
        ]
    },

    "Coal Mine": {
        "req": [],
        "mak": [
            ("COAL", 1)
        ]
    },

    "Water Pump": {
        "req": [],
        "mak": [
            ("WATER", 10)
        ]
    },

    "Steam Turbine": {
        "req": [
            ("STEAM", 100)
        ],
        "mak": [
            ("POWER", 100000)
        ]
    },

    "Gook Fabricator": {
        "req": [
            ("POWER", 3)
        ],
        "mak": [
            ("GOOK", 3)
        ]
    },
}
