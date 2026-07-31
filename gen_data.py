import urllib.request, json

url = 'https://raw.githubusercontent.com/tylercamp/palcalc/main/PalCalc.Model/db.json'
data = json.loads(urllib.request.urlopen(url).read())

lines = ['# Auto-generated from palcalc db.json', '# {internal_name: (english_name, breeding_power, internal_index, is_variant, image_id)}', '', 'PALS = {']
for i, p in enumerate(data['Pals']):
    iname = p['InternalName']
    ename = p['Name'].replace('"', '\\"')
    bp = p['BreedingPower']
    idx = -p.get('BreedingPowerPriority', bp * 100) # Negative because breeding engine picks smallest index, but we want highest priority
    is_variant = 1 if p['Id']['IsVariant'] else 0
    
    paldex_num = p['Id']['PalDexNo']
    suffix = "B" if is_variant else ""
    image_id = f"{paldex_num:03d}{suffix}"
    
    lines.append(f'    "{iname}": ("{ename}", {bp}, {idx}, {is_variant}, "{image_id}"),')
lines.append('}')

with open(r'c:\Users\Nolann\Desktop\palbreeder\pal_data.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f'Generated pal_data.py with {len(data["Pals"])} Pals')
