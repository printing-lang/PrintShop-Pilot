import os
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
import qtawesome as qta

from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QUrl

# Path to assets directory
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")

def get_icon(name, color=None):
    """
    Load an icon by name.
    First checks for a local PNG in assets/icons.
    Then checks in Google Icons directory.
    If not found, falls back to qtawesome (FontAwesome).
    
    Args:
        name (str): Filename (without extension) or FontAwesome name (e.g. "fa5s.home")
        color (str): Hex color for FontAwesome icons. Ignored for PNGs.
    """
    # Check for local PNG in assets/icons first
    png_path = os.path.join(ICONS_DIR, f"{name}.png")
    if os.path.exists(png_path):
        if color:
            # Manually colorize the PNG
            pixmap = QPixmap(png_path)
            painter = QPainter(pixmap)
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.fillRect(pixmap.rect(), QColor(color))
            painter.end()
            return QIcon(pixmap)
        return QIcon(png_path)
    
    # Check for Google Icons
    google_icons_dir = r"C:\Users\PC\Downloads\Antigravity\Assets\Google Icons"
    google_icon_path = os.path.join(google_icons_dir, f"{name}.png")
    if os.path.exists(google_icon_path):
        if color:
            # Manually colorize the PNG
            pixmap = QPixmap(google_icon_path)
            painter = QPainter(pixmap)
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.fillRect(pixmap.rect(), QColor(color))
            painter.end()
            return QIcon(pixmap)
        return QIcon(google_icon_path)
        
    # Fallback to qtawesome
    if color:
        return qta.icon(name, color=color)
    return qta.icon(name)

def get_image_path(name):
    """Get absolute path to an image in assets/images"""
    return os.path.join(IMAGES_DIR, name)

def play_sound(name):
    """
    Play a sound effect from assets/sounds.
    Args:
        name (str): Filename without extension (e.g. "select")
    """
    path = os.path.join(SOUNDS_DIR, f"{name}.wav")
    if os.path.exists(path):
        effect = QSoundEffect()
        effect.setSource(QUrl.fromLocalFile(path))
        effect.setVolume(0.5)
        effect.play()
        # Keep reference to prevent garbage collection while playing
        # In a real app, we might want a SoundManager class to handle this better
        return effect 
    return None
