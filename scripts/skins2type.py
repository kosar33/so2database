import pandas as pd
import json
import os
import re
import sys


def main():
    try:
        # File paths
        input_path = 'data/data.json'
        output_path = 'data/id2type.json'

        # Checking the existence of a file
        if not os.path.exists(input_path):
            print(f"Error: Input file not found at {input_path}")
            sys.exit(1)

        # Uploading data
        df = pd.read_json(input_path)
        print(f"Loaded {len(df)} items from {input_path}")

        # Search Dictionary
        search_dict = {
            "Брелоки": ("Chibi \"", "Charm \""),
            "Винтовки": ("AKR \"", "AKR12 \"", "FAMAS \"", "FN FAL \"", "M16 \"", "M4 \"", "M4A1 \"", "VAL \""),
            "Гранаты": ("HE \"", "Smoke \"", "Flash \"", "Molotov \"", "Thermite \""),
            "Граффити": ("Graffiti \"",),
            "Контейнеры": (
            "\" Box", "\" Case", "\" Charm Pack", "Gift Box", "\" Gloves Case", "Graffiti Pack", "\" Knife Case",
            "Sticker Pack", "\" Weapon Box", "\" Weapon Case", "\" Crate", "\" Gift Case", "Fragment Box"),
            "Наклейки": ("Sticker \"",),
            "Ножи": ("Butterfly \"", "Dual Daggers \"", "Fang \"", "Flip \"", "jKommando \"", "Karambit \"", "Kukri \"",
                     "Kunai \"", "M9 Bayonet \"", "Mantis \"", "Scorpion \"", "Stiletto \"", "Sting \"", "Tanto \""),
            "Перчатки": ("Gloves \"",),
            "Пистолеты": ("Berettas \"", "Desert Eagle \"", "F/S \"", "G22 \"", "P350 \"", "TEC-9 \"", "USP \""),
            "ПП": ("Akimbo Uzi \"", "MAC10 \"", "MP5 \"", "MP7 \"", "P90 \"", "UMP45 \""),
            "Снайперские": ("AWM \"", "M110 \"", "M40 \""),
            "Тяжелое": ("FabM \"", "M60 \"", "SM1014 \"", "SPAS \""),
            "Фрагменты": (" Fragment",),
            "Медали": ("Medal",)
        }

        result = []
        total_items = 0

        for type_ru, patterns in search_dict.items():
            ids = []
            for pattern in patterns:
                if type_ru == "Медали":
                    mask = df['name'].apply(
                        lambda x: bool(re.search(rf'\b{re.escape(pattern)}\b', str(x), flags=re.IGNORECASE)))
                else:
                    mask = df['name'].str.contains(pattern, case=True, regex=False, na=False)

                    ids.extend(df.loc[mask, 'id'].astype(int).tolist())

                    unique_ids = sorted(set(ids))

                    if type_ru == "Контейнеры" and 5101 in unique_ids:
                        unique_ids.remove(5101)

                    id_string = ",".join(map(str, unique_ids))
                    item_count = len(unique_ids)
                    total_items += item_count

                    result.append({
                        "ids": id_string,
                        "type_ru": type_ru,
                        "item_count": item_count
                    })

                    # Sorting by number of items
                    result.sort(key=lambda x: x["item_count"], reverse=True)

                    # Saving the results
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)

                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)

                    print(f"Successfully updated {output_path}")
                    print(f"Total categories: {len(result)}")
                    print(f"Total items: {total_items}")

                    # Checking coverage
                    coverage = total_items / len(df) * 100
                    print(f"Coverage: {coverage:.2f}%")

                    if coverage < 90:
                        print("Warning: Coverage is below 90%!")
                    sys.exit(2)

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()