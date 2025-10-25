import { TextToSpeech } from '@capacitor-community/text-to-speech';
import { Capacitor } from '@capacitor/core';

export class TTSService {
  static async requestPermissions(): Promise<boolean> {
    try {
      if (Capacitor.isNativePlatform()) {
        // For mobile, permissions are typically handled automatically
        // but we can check if TTS is available
        const isSupported = await TextToSpeech.isLanguageSupported({ lang: 'en-US' });
        return isSupported.value;
      }
      return true;
    } catch (error) {
      console.error('TTS permission error:', error);
      return false;
    }
  }
  static async speak(text: string): Promise<void> {
    console.log('TTS: Attempting to speak:', text);
    console.log('TTS: Platform is native:', Capacitor.isNativePlatform());
    
    try {
      if (Capacitor.isNativePlatform()) {
        console.log('TTS: Using Capacitor plugin');
        
        // Check if TTS is supported
        const isSupported = await TextToSpeech.isLanguageSupported({ lang: 'en-US' });
        console.log('TTS: Language supported:', isSupported);
        
        await TextToSpeech.speak({
          text: text,
          lang: 'en-US',
          rate: 1.0,
          pitch: 1.0,
          volume: 1.0,
          category: 'ambient'
        });
        console.log('TTS: Capacitor speak completed');
      } else {
        console.log('TTS: Using Web Speech API');
        
        if ('speechSynthesis' in window) {
          // Wait for voices to load
          const voices = speechSynthesis.getVoices();
          console.log('TTS: Available voices:', voices.length);
          
          if (voices.length === 0) {
            // Wait for voices to load
            await new Promise(resolve => {
              speechSynthesis.addEventListener('voiceschanged', resolve, { once: true });
              setTimeout(resolve, 1000); // Fallback timeout
            });
          }
          
          const utterance = new SpeechSynthesisUtterance(text);
          utterance.lang = 'en-US';
          utterance.rate = 1.0;
          utterance.pitch = 1.0;
          utterance.volume = 1.0;
          
          // Add event listeners for debugging
          utterance.onstart = () => console.log('TTS: Speech started');
          utterance.onend = () => console.log('TTS: Speech ended');
          utterance.onerror = (e) => console.error('TTS: Speech error:', e);
          
          speechSynthesis.speak(utterance);
          console.log('TTS: Web speech initiated');
        } else {
          console.error('TTS: Speech synthesis not supported');
          throw new Error('Speech synthesis not supported');
        }
      }
    } catch (error) {
      console.error('Text-to-speech error:', error);
      throw error;
    }
  }

  static async stop(): Promise<void> {
    console.log('TTS: Stopping speech');
    try {
      if (Capacitor.isNativePlatform()) {
        await TextToSpeech.stop();
        console.log('TTS: Capacitor stop completed');
      } else {
        if ('speechSynthesis' in window) {
          speechSynthesis.cancel();
          console.log('TTS: Web speech cancelled');
        }
      }
    } catch (error) {
      console.error('TTS stop error:', error);
    }
  }
}