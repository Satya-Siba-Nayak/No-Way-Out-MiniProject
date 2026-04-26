import os
import xml.etree.ElementTree as ET

def remap_and_find_missing(map_dir):
    print(f"Processing TSX files in {map_dir}")
    tsx_files = [f for f in os.listdir(map_dir) if f.endswith('.tsx')]
    
    local_files = set(os.listdir(map_dir))
    strictly_missing = set()
    
    for tsx_file in tsx_files:
        tsx_path = os.path.join(map_dir, tsx_file)
        try:
            tree = ET.parse(tsx_path)
            root = tree.getroot()
            modified = False
            
            for image in root.findall('image'):
                source = image.get('source')
                if not source: continue
                
                # Full path based on TSX location
                full_path = os.path.normpath(os.path.join(map_dir, source))
                
                if os.path.exists(full_path):
                    # It exists, no need to touch
                    continue
                
                # Check if it exists locally in the map_dir
                basename = os.path.basename(source)
                if basename in local_files:
                    # Update to local relative path
                    image.set('source', basename)
                    modified = True
                    print(f"Remapped {source} -> {basename} in {tsx_file}")
                else:
                    # Strictly missing
                    strictly_missing.add(basename)
            
            if modified:
                tree.write(tsx_path, encoding="UTF-8", xml_declaration=True)
                
        except Exception as e:
            print(f"Error parsing {tsx_file}: {e}")

    print("\n--- STRICTLY MISSING FILES (Please find and paste these into the folder) ---")
    for missing in sorted(strictly_missing):
        print(missing)

remap_and_find_missing(r'c:\Users\ssnay\Documents\GitHub\No-Way-Out-MiniProject\Maps\level 3 - test')
