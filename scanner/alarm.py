"""Alarm system for quality failures."""

import os
import threading
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AlarmSystem:
    """Handles visual and audio alarms for scan failures."""
    
    def __init__(self, enable_audio: bool = True, enable_visual: bool = True):
        self.enable_audio = enable_audio
        self.enable_visual = enable_visual
        self.audio_file: Optional[str] = None
        self.is_active: bool = False
        
    def set_audio_file(self, filepath: str):
        """Set the audio file path for alarm sound."""
        if os.path.exists(filepath):
            self.audio_file = filepath
            logger.info(f"Alarm sound set: {filepath}")
        else:
            logger.warning(f"Alarm sound file not found: {filepath}")
    
    def trigger_alarm(self, is_failure: bool):
        """Trigger alarm (visual and/or audio)."""
        if not is_failure:
            return
            
        self.is_active = True
        
        if self.enable_visual:
            self._trigger_visual_alarm()
        
        if self.enable_audio and self.audio_file:
            self._trigger_audio_alarm()
    
    def _trigger_visual_alarm(self):
        """Trigger visual alarm (implemented in UI layer)."""
        # Visual alarm is handled by the UI
        # This method can be used to update state
        logger.debug("Visual alarm triggered")
    
    def _trigger_audio_alarm(self):
        """Play alarm sound in a separate thread."""
        def play_sound():
            try:
                import winsound
                winsound.PlaySound(self.audio_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
                logger.debug("Alarm sound played")
            except Exception as e:
                logger.error(f"Audio playback error: {e}")
        
        if self.audio_file:
            thread = threading.Thread(target=play_sound, daemon=True)
            thread.start()
    
    def stop_alarm(self):
        """Stop any active alarm."""
        self.is_active = False
        try:
            import winsound
            winsound.PlaySound(None, winsound.SND_PURGE)
        except:
            pass
    
    def test_alarm(self):
        """Test alarm system."""
        logger.info("Testing alarm system...")
        self.trigger_alarm(True)
        # Auto-stop after 1 second
        import threading
        t = threading.Timer(1.0, self.stop_alarm)
        t.daemon = True
        t.start()
