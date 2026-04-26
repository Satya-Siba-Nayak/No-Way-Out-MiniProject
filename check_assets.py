import os
import xml.etree.ElementTree as ET

def check_assets(map_dir):
    print(f"Checking assets in {map_dir}")
    tmx_files = [f for f in os.listdir(map_dir) if f.endswith('.tmx')]
    
    used_tsx = set()
    used_images = set()
    missing_files = []
    
    for tmx_file in tmx_files:
        tmx_path = os.path.join(map_dir, tmx_file)
        tree = ET.parse(tmx_path)
        root = tree.getroot()
        
        for tileset in root.findall('tileset'):
            source = tileset.get('source')
            if source:
                tsx_path = os.path.normpath(os.path.join(map_dir, source))
                used_tsx.add(tsx_path)
                
                if not os.path.exists(tsx_path):
                    missing_files.append(tsx_path)
                else:
                    tsx_tree = ET.parse(tsx_path)
                    tsx_root = tsx_tree.getroot()
                    for image in tsx_root.findall('image'):
                        img_source = image.get('source')
                        if img_source:
                            img_path = os.path.normpath(os.path.join(os.path.dirname(tsx_path), img_source))
                            used_images.add(img_path)
                            if not os.path.exists(img_path):
                                missing_files.append(img_path)

    all_files = set(os.path.normpath(os.path.join(map_dir, f)) for f in os.listdir(map_dir) if os.path.isfile(os.path.join(map_dir, f)))
    unused_files = all_files - used_tsx - used_images
    # remove tmx from unused
    for tmx in tmx_files:
        unused_files.discard(os.path.normpath(os.path.join(map_dir, tmx)))

    print("Missing files:")
    for m in sorted(missing_files):
        print("  " + m)
        
    print("\nUsed images:")
    for u in sorted(used_images):
        print("  " + u)
        
    print("\nUnused files in directory:")
    for u in sorted(unused_files):
        print("  " + u)

check_assets(r'c:\Users\ssnay\Documents\GitHub\No-Way-Out-MiniProject\Maps\level 3 - test')
