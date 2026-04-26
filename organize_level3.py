import os
import shutil
import xml.etree.ElementTree as ET

def organize_level3():
    base_dir = r"c:\Users\ssnay\Documents\GitHub\No-Way-Out-MiniProject\Maps"
    old_map_dir = os.path.join(base_dir, "level 3 - test")
    new_map_dir = os.path.join(base_dir, "Level 3")
    
    # 1. Rename directory
    if os.path.exists(old_map_dir):
        try:
            # Need to handle case where Level 3 already exists
            if not os.path.exists(new_map_dir):
                os.rename(old_map_dir, new_map_dir)
            else:
                print(f"Warning: {new_map_dir} already exists. Operating on it directly.")
        except Exception as e:
            print(f"Rename failed: {e}. Will operate on {old_map_dir} instead.")
            new_map_dir = old_map_dir
    elif not os.path.exists(new_map_dir):
        print("Level 3 directory not found!")
        return
        
    assets_dir = os.path.join(new_map_dir, "assets")
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        
    tmx_path = os.path.join(new_map_dir, "DungeonLevel3.tmx")
    if not os.path.exists(tmx_path):
        print(f"Could not find {tmx_path}")
        return
        
    # 2. Parse TMX
    tree = ET.parse(tmx_path)
    root = tree.getroot()
    
    used_tsx_names = set()
    used_img_names = set()
    
    for tileset in root.findall('tileset'):
        source = tileset.get('source')
        if source:
            tsx_basename = os.path.basename(source)
            used_tsx_names.add(tsx_basename)
            # Update TMX to point to assets folder
            tileset.set('source', f"assets/{tsx_basename}")
            
    # Write updated TMX
    tree.write(tmx_path, encoding="UTF-8", xml_declaration=True)
    
    # 3. Parse and update TSX files
    for tsx_name in used_tsx_names:
        # It could be in root or already in assets
        tsx_root_path = os.path.join(new_map_dir, tsx_name)
        tsx_assets_path = os.path.join(assets_dir, tsx_name)
        
        current_tsx_path = None
        if os.path.exists(tsx_root_path):
            current_tsx_path = tsx_root_path
        elif os.path.exists(tsx_assets_path):
            current_tsx_path = tsx_assets_path
            
        if current_tsx_path:
            try:
                tsx_tree = ET.parse(current_tsx_path)
                tsx_root = tsx_tree.getroot()
                
                for image in tsx_root.findall('image'):
                    img_source = image.get('source')
                    if img_source:
                        img_basename = os.path.basename(img_source)
                        used_img_names.add(img_basename)
                        # TSX and PNG will both be in assets/, so relative path is just basename
                        image.set('source', img_basename)
                        
                tsx_tree.write(current_tsx_path, encoding="UTF-8", xml_declaration=True)
                
                # Move TSX if it's not already in assets
                if current_tsx_path == tsx_root_path:
                    shutil.move(tsx_root_path, tsx_assets_path)
            except Exception as e:
                print(f"Error processing {current_tsx_path}: {e}")
        else:
            print(f"Warning: TSX file missing entirely: {tsx_name}")
            
    # 4. Move used PNGs to assets
    for img_name in used_img_names:
        img_root_path = os.path.join(new_map_dir, img_name)
        img_assets_path = os.path.join(assets_dir, img_name)
        
        if os.path.exists(img_root_path):
            shutil.move(img_root_path, img_assets_path)
        elif not os.path.exists(img_assets_path):
            print(f"Warning: Missing PNG file: {img_name} (needs to be placed in {assets_dir})")
            
    # 5. Delete unused TSX and PNG files in the root new_map_dir
    all_files = os.listdir(new_map_dir)
    deleted_count = 0
    for f in all_files:
        path = os.path.join(new_map_dir, f)
        if os.path.isfile(path):
            if f.endswith('.tsx') or f.endswith('.png') or f.endswith('.jpg'):
                # Note: f shouldn't be in used_tsx_names or used_img_names if we successfully moved them,
                # but let's double check.
                if f not in used_tsx_names and f not in used_img_names:
                    try:
                        os.remove(path)
                        deleted_count += 1
                    except Exception as e:
                        print(f"Could not delete {f}: {e}")
                        
    print(f"Organization complete! Moved used files to assets/ and deleted {deleted_count} unused files.")

if __name__ == "__main__":
    organize_level3()
