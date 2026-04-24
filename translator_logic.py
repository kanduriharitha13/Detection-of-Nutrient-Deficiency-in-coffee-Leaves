# backend/translator_logic.py
from deep_translator import GoogleTranslator

def translate_text(text: str, target_lang: str):
    """
    NLP logic to translate deficiency names and remedies.
    Target lang examples: 'hi' (Hindi), 'te' (Telugu), 'kn' (Kannada), 'es' (Spanish).
    """
    try:
        # We use GoogleTranslator via deep-translator because it's fast and free
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return translated
    except Exception as e:
        print(f"Translation Error: {e}")
        return text # Return original text if translation fails