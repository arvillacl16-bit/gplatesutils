new_components = []
with open('rotation.rot') as f:
    components = [r.split() for r in f.readlines()]
    for i, line in enumerate(components):
        new_components.append(line)
        if i + 1 < len(components) and float(components[i + 1][1]) != 1.0 and [float(angle) for angle in components[i + 1][2:5]] != [90.0, 0.0, 0.0]:
            next_line = components[i + 1]
            new_line = []
            new_line.append(next_line[0])
            new_line.append("1.0")
            new_line.extend(next_line[2:5])
            new_line.extend(next_line[5:])

with open('rotation.rot', 'w') as f:
    for line in new_components:
        f.write(' '.join(line) + '\n')
