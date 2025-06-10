import json

INPUT_FILE = 'Labs/Lab2/font.json'
OUTPUT_FILE = 'Labs/Lab2/font.txt'

with open(INPUT_FILE, 'r') as source:
    font_data = json.load(source)

with open(OUTPUT_FILE, 'w') as target:
    # Примерный размер
    target.write("5\n5\n")  
    for char, lines in font_data.items():
        for line in lines:
            target.write(line + '\n')
        target.write('-' * 15 + '\n')
