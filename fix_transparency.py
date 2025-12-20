import pygame as pg
import sys
import os

def remove_black_background(image_path):
    try:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pg.init()
        pg.display.set_mode((1, 1))
        
        # Load image
        image = pg.image.load(image_path).convert_alpha()
        width, height = image.get_size()
        
        # Create new surface with alpha channel
        new_image = pg.Surface((width, height), pg.SRCALPHA)
        new_image.fill((0, 0, 0, 0)) # Fill with transparent
        
        # Lock surfaces for pixel access
        image.lock()
        new_image.lock()
        
        # Iterate pixels
        for x in range(width):
            for y in range(height):
                color = image.get_at((x, y))
                # Check for black (allow small tolerance if needed, but sticking to exact black for generated art)
                if color.r < 10 and color.g < 10 and color.b < 10:
                    new_image.set_at((x, y), (0, 0, 0, 0))
                else:
                    new_image.set_at((x, y), (color.r, color.g, color.b, 255))
                    
        image.unlock()
        new_image.unlock()
        
        # Save back to same path
        pg.image.save(new_image, image_path)
        print(f"Fixed transparency for {image_path}")
        
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_transparency.py <file1> <file2> ...")
        sys.exit(1)
        
    for path in sys.argv[1:]:
        remove_black_background(path)
