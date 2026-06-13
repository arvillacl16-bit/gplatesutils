import sys

class Line:
    def __init__(self, line_str: str):
        components_str = line_str.split()
        self.plate_id = int(components_str[0])
        self.time = float(components_str[1])
        self.lat = float(components_str[2])
        self.lon = float(components_str[3])
        self.angle = float(components_str[4])
        self.conjugate_id = int(components_str[5])

    def __str__(self):
        return f"{self.plate_id:<4} {self.time:>6.2f} {self.lat:>7.2f} {self.lon:>7.2f} {self.angle:>7.2f} {self.conjugate_id:<4} !"


try:
    with open('rotation.rot', 'r') as f:
        lines = [Line(line_str) for line_str in f.readlines() if line_str.strip() and not line_str.strip().startswith('!')]
except FileNotFoundError:
    print("Error: 'rotation.rot' file not found.")
    sys.exit(1)

while True:
    try:
        user_input = input("What is the ID of the continent you are rifting from (Parent)? ")
        parent_id = int(user_input)
        if parent_id == 999:
            print("Lines starting with 999 are ignored by GPlates.")
            continue
        break
    except ValueError:
        continue

while True:
    try:
        user_input = input("What is the ID of the continent you are rifting off (Rifted)? ")
        rifted_id = int(user_input)
        if rifted_id == 999:
            print("Lines starting with 999 are ignored by GPlates.")
            continue
        break
    except ValueError:
        continue

while True:
    try:
        user_input = input("What is the time that the continents rift (Ma)? ")
        time_of_rift = float(user_input)
        if time_of_rift < 1.0:
            print("Times less than 1 Ma are reserved for drift corrections.")
            continue
        break
    except ValueError:
        continue

parent_pole = None

for line in lines:
    if line.plate_id == parent_id and line.time == time_of_rift:
        parent_pole = line
        break

if not parent_pole:
    print(f"Error: Could not find a rotation line for parent plate {parent_id} at {time_of_rift} Ma.")
    sys.exit(1)

if parent_pole.conjugate_id != 0:
    print(f"Warning: Parent plate {parent_id} is already attached to plate {parent_pole.conjugate_id} at {time_of_rift} Ma.")

print(f"\n[Auto-Detected] Found parent plate {parent_id} motion parameters at {time_of_rift} Ma:")
print(f"  Latitude: {parent_pole.lat}, Longitude: {parent_pole.lon}, Angle: {parent_pole.angle}")

conjugates_of_rifted = []
while True:
    try:
        user_input = input("Type in a conjugate ID for the rifted plate (or q to skip/exit): ")
        if user_input.lower() in ('q', 'quit'):
            break
        conjugates_of_rifted.append(int(user_input))
    except ValueError:
        continue


generated_lines = []

pre_rift_line = Line(f"{rifted_id} {time_of_rift} {parent_pole.lat} {parent_pole.lon} {parent_pole.angle} {parent_id}")
generated_lines.append(pre_rift_line)

post_rift_line_present = Line(f"{rifted_id} 0.0 90.0 0.0 0.0 0")
generated_lines.append(post_rift_line_present)


output_filename = 'rotation.rot'
with open(output_filename, 'w') as f:
    for line in lines:
        if line.plate_id == rifted_id and line.time == time_of_rift:
            continue
        f.write(str(line) + "\n")
        
    for line in generated_lines:
        f.write(str(line) + "\n")

