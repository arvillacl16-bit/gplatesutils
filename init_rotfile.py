class Continent:
    def __init__(self, plate_id: int):
        self.plate_id = plate_id
        self.conjugate_ids = []
    
time = 0
while True:
    user_input = input("What is your starting time? ")
    try:
        time = float(user_input)
        if time < 1:
            print("Starting time must be before 1 Ma, as 1 Ma is when drift correction stops.")
            continue
        break
    except ValueError:
        continue

continents = []
ids = set()

while True:
    user_input = input("Enter a plate ID (type in q or quit to finish entering them): ")
    if user_input in ('q', 'quit'):
        break
    try:
        plate_id = int(user_input)
        if plate_id == 999:
            print("In a .rot file, lines starting with 999 are ignored, so that plate ID does nothing.")
            continue
        if plate_id in ids:
            print("You already have this ID.")
            continue
        ids.add(plate_id)
        continent = Continent(plate_id)
        while True:
            new_user_input = input("Enter a conjugate plate ID (type in q or quit to finish entering them): ")
            if new_user_input in ('q', 'quit'):
                break
            try:
                conjugate_plate_id = int(new_user_input)
                if conjugate_plate_id == 999:
                    print("In a .rot file, lines starting with 999 are ignored, so that plate ID does nothing.")
                    continue
                if conjugate_plate_id in ids:
                    print("You already have this ID.")
                    continue
                ids.add(conjugate_plate_id)
                continent.conjugate_ids.append(conjugate_plate_id)
            except ValueError:
                continue

        continents.append(continent)
    except ValueError:
        continue

with open("rotation.rot", 'w+') as f:
    for continent in continents:
        f.write(f"{continent.plate_id} 0.0 90.0 0.0 0.0 000 !\n{continent.plate_id} {time:.2f} 90.0 0.0 0.0 000 !\n")
        for conjugate_id in continent.conjugate_ids:
            f.write(f"{conjugate_id} 0.0 90.0 0.0 0.0 {continent.plate_id} !\n{conjugate_id} {time:.2f} 90.0 0.0 0.0 {continent.plate_id} !\n")
