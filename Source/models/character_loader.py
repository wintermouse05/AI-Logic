"""
Sprite Loader for Wumpus World
Loads PNG sprites for agent and game objects with transparent backgrounds
"""

import pygame
import os
from typing import Optional

class SpriteLoader:
    """Loads game sprites from PNG files"""
    
    def __init__(self):
        self.models_dir = os.path.dirname(os.path.abspath(__file__))
        self.sprites = {}
        self.load_sprites()
    
    def load_sprites(self):
        """Load all sprites from PNG files"""
        
        # Map sprite names to PNG filenames
        sprite_files = {
            'agent': 'agent.png',
            'wumpus': 'wumpus.png',
            'gold': 'gold.png',
            'hole': 'hole.png',
            'Death_skull': 'Death_skull.png'
        }
        
        for sprite_name, filename in sprite_files.items():
            file_path = os.path.join(self.models_dir, filename)
            
            if os.path.exists(file_path):
                try:
                    # Load sprite with transparency support
                    sprite = pygame.image.load(file_path).convert_alpha()
                    self.sprites[sprite_name] = sprite
                    
                except pygame.error as e:
                    print(f"Error loading {filename}: {e}")
    
    def get_sprite(self, sprite_name: str, size: Optional[int] = None) -> Optional[pygame.Surface]:
        """Get sprite by name, optionally scaled to size"""
        if sprite_name in self.sprites:
            sprite = self.sprites[sprite_name]
            
            if size and size != sprite.get_width():
                # Scale sprite while maintaining aspect ratio and transparency
                return pygame.transform.scale(sprite, (size, size))
            
            return sprite
        
        return None
    
    def sprite_exists(self, sprite_name: str) -> bool:
        """Check if sprite exists"""
        return sprite_name in self.sprites

# Global sprite loader instance
sprite_loader = None

def init_sprite_loader():
    """Initialize the sprite loader"""
    global sprite_loader
    if sprite_loader is None:
        sprite_loader = SpriteLoader()

def get_sprite(sprite_name: str, size: Optional[int] = None) -> Optional[pygame.Surface]:
    """Convenience function to get sprite"""
    init_sprite_loader()
    return sprite_loader.get_sprite(sprite_name, size)

def get_agent_sprite(size: Optional[int] = None, filename: Optional[str] = None) -> Optional[pygame.Surface]:
    """Get agent sprite by direction image"""
    init_sprite_loader()
    if filename:
        # Tìm file ảnh theo tên trong thư mục models
        import os
        import pygame
        img_path = os.path.join(os.path.dirname(__file__), filename)
        if os.path.exists(img_path):
            img = pygame.image.load(img_path)
            if size:
                img = pygame.transform.scale(img, (size, size))
            return img
        else:
            return sprite_loader.get_sprite('agent', size)
    else:
        return sprite_loader.get_sprite('agent', size)

def get_wumpus_sprite(size: Optional[int] = None) -> Optional[pygame.Surface]:
    """Get wumpus sprite"""
    return get_sprite('wumpus', size)

def get_gold_sprite(size: Optional[int] = None) -> Optional[pygame.Surface]:
    """Get gold sprite"""
    return get_sprite('gold', size)

def get_death_skull_sprite(size: Optional[int] = None) -> Optional[pygame.Surface]:
    """Get death skull sprite"""
    return get_sprite('Death_skull', size)

def get_hole_sprite(size: Optional[int] = None) -> Optional[pygame.Surface]:
    """Get hole/pit sprite"""
    return get_sprite('hole', size)

if __name__ == "__main__":
    # Test the sprite loader
    pygame.init()
    pygame.display.set_mode((1, 1))  # Minimal display for testing
    
    print("Sprite Loader Test")
    print("=" * 30)
    
    loader = SpriteLoader()
    
    sprites = ['agent', 'wumpus', 'gold', 'hole']
    for sprite_name in sprites:
        sprite = loader.get_sprite(sprite_name)
        if sprite:
            print(f"  {sprite_name}: {sprite.get_size()} pixels")
        else:
            print(f"  {sprite_name}: Failed to load")
    
    print("\nAll sprites loaded successfully!" if len(loader.sprites) == 4 else f"Loaded {len(loader.sprites)}/4 sprites")
