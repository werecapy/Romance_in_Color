# List of tags as subgenres
tags = [
    "fantasy", "high fantasy", "urban fantasy", "steampunk",
    "paranormal", "magic", "time travel", "angels", "demons",
    "fae", "monsters", "orcs", "shapeshifters", "werewolves",
    "dragon shifter", "bear shifter", "lion shifter", "tiger shifter",
    "vampires", "witches", "science fiction", "aliens", "dark romance",
    "young adult", "new adult", "mystery", "suspense", "dystopian",
    "omegaverse", "humor", "angst", "horror"
]

# Define subgenres as categories
subgenres = {
    "Fantasy": ["fantasy", "high fantasy", "urban fantasy", "steampunk"],
    "Paranormal": ["paranormal", "magic", "time travel", "angels", "demons", "fae", "monsters", "orcs", "shapeshifters",
                   "werewolves", "dragon shifter", "bear shifter", "lion shifter", "tiger shifter", "vampires",
                   "witches"],
    "Science Fiction": ["science fiction", "aliens"],
    "Romance": ["dark romance", "young adult", "new adult", "omegaverse"],
    "Mystery & Suspense": ["mystery", "suspense", "dystopian"],
    "Humor & Angst": ["humor", "angst"],
    "Horror": ["horror"]
}


# Function to classify tags
def classify_tags(tags, subgenres):
    classified = {}

    for tag in tags:
        found = False
        for genre, genre_tags in subgenres.items():
            if tag in genre_tags:
                if genre not in classified:
                    classified[genre] = []
                classified[genre].append(tag)
                found = True
                break
        if not found:
            classified["Uncategorized"] = classified.get("Uncategorized", []) + [tag]

    return classified


# Classify the tags
classified_tags = classify_tags(tags, subgenres)

# Print the classified tags
for genre, tags in classified_tags.items():
    print(f"{genre}: {', '.join(tags)}")
