import os
import xml.etree.ElementTree as ET

def find_missing_in_assets(map_dir):
    assets_dir = os.path.join(map_dir, 'assets')
    tmx_path = os.path.join(map_dir, 'DungeonLevel3.tmx')
    
    if not os.path.exists(tmx_path):
        print(f"TMX not found: {tmx_path}")
        return
        
    tree = ET.parse(tmx_path)
    root = tree.getroot()
    
    missing = []
    
    for tileset in root.findall('tileset'):
        source = tileset.get('source')
        if not source: continue
        
        tsx_path = os.path.join(map_dir, source)
        if not os.path.exists(tsx_path):
            missing.append(f"TSX missing: {source}")
            continue
            
        tsx_tree = ET.parse(tsx_path)
        tsx_root = tsx_tree.getroot()
        
        for image in tsx_root.findall('image'):
            img_source = image.get('source')
            if not img_source: continue
            
            img_path = os.path.join(os.path.dirname(tsx_path), img_source)
            if not os.path.exists(img_path):
                missing.append(f"Image missing for {os.path.basename(tsx_path)}: {img_source}")
                
    if missing:
        print("STILL MISSING FILES:")
        for m in sorted(set(missing)):
            print(m)
    else:
        print("ALL FILES FOUND AND MAPPED CORRECTLY!")

find_missing_in_assets(r'c:\Users\ssnay\Documents\GitHub\No-Way-Out-MiniProject\Maps\Level 3')
