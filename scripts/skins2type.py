import pandas as pd
import json
import os
import re
import sys

def main():
    try:
        # File paths
        input_path = 'data/skins.json'
        output_path = 'data/id2type.json'
        # missing_path = 'log/missing_ids.txt'  # Файл для ненайденных ID

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
            "Наклейки": ("Sticker \"", "Shield \""),
            "Ножи": ("Butterfly \"", "Dual Daggers \"", "Fang \"", "Flip \"", "jKommando \"", "Karambit \"", "Kukri \"",
                     "Kunai \"", "M9 Bayonet \"", "Mantis \"", "Scorpion \"", "Stiletto \"", "Sting \"", "Tanto \""),
            "Перчатки": ("Gloves \"",),
            "Пистолеты": ("Berettas \"", "Desert Eagle \"", "F/S \"", "G22 \"", "P350 \"", "TEC-9 \"", "USP \""),
            "ПП": ("Akimbo Uzi \"", "MAC10 \"", "MP5 \"", "MP7 \"", "P90 \"", "UMP45 \""),
            "Снайперские": ("AWM \"", "M110 \"", "M40 \""),
            "Тяжелое": ("FabM \"", "M60 \"", "SM1014 \"", "SPAS \""),
            "Фрагменты": (" Fragment",),
            "Медали": ("Medal",),
            "Рамки": ("Frame",)
        }

        result = []
        all_found_ids = set()
        all_ids = set(df['id'].astype(int).tolist())  # Все ID в базе

        for type_ru, patterns in search_dict.items():
            ids = []
            for pattern in patterns:
                if type_ru in ["Медали", "Рамки"]:
                    mask = df['name'].apply(
                        lambda x: bool(re.search(rf'\b{re.escape(pattern)}\b', str(x), flags=re.IGNORECASE)))
                else:
                    mask = df['name'].str.contains(pattern, case=True, regex=False, na=False)
                
                # Собираем ID для текущего паттерна
                found = df.loc[mask, 'id'].astype(int).tolist()
                ids.extend(found)

            # Обработка ID для категории после сбора всех паттернов
            unique_ids = sorted(set(ids))
            
            # Исключение для контейнеров
            if type_ru == "Контейнеры" and 5101 in unique_ids:
                unique_ids.remove(5101)
            
            id_string = ",".join(map(str, unique_ids))
            item_count = len(unique_ids)
            
            # Сохраняем для категории
            result.append({
                "ids": id_string,
                "type_ru": type_ru,
                "item_count": item_count
            })
            
            # Собираем все найденные ID
            all_found_ids.update(unique_ids)
            
            # print(f"Processed {type_ru}: found {item_count} items")

        # Находим ненайденные ID
        missing_ids = sorted(all_ids - all_found_ids)
        missing_ids_str = ",".join(map(str, missing_ids))
        
        # Сохранение результатов
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        # Сохранение ненайденных ID
        # with open(missing_path, 'w', encoding='utf-8') as f:
        #     f.write(missing_ids_str)
        
        # Статистика
        total_items = len(all_found_ids)
        unique_coverage = total_items / len(df) * 100
        
        print(f"\nSuccessfully updated {output_path}")
        print(f"Total categories: {len(result)}")
        print(f"Unique items covered: {total_items}")
        print(f"Coverage: {unique_coverage:.2f}%")
        # print(f"Missing IDs saved to: {missing_path}")
        print(f"Missing IDs count: {len(missing_ids)}")
        print(f"Missing IDs: {missing_ids_str}")

        if unique_coverage < 90:
            print("\nWarning: Coverage is below 90%!")
            sys.exit(2)
        else:
            sys.exit(0)

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()