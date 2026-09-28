from typing import List, Dict, Any, Optional

# Canonical Gemini-Supported Languages Catalog
# Covers text models and marks high-fidelity bidirectional Gemini Multimodal Live voice-capable languages.

SUPPORTED_LANGUAGES: List[Dict[str, Any]] = [
    {
        "code": "client",
        "name": "Device Default (Auto-Detect)",
        "native_name": "Automatic",
        "voice_supported": True,
    },
    # Primary Voice-Ready Languages
    {"code": "en", "name": "English", "native_name": "English", "voice_supported": True},
    {"code": "es", "name": "Spanish", "native_name": "Español", "voice_supported": True},
    {"code": "fr", "name": "French", "native_name": "Français", "voice_supported": True},
    {"code": "de", "name": "German", "native_name": "Deutsch", "voice_supported": True},
    {"code": "it", "name": "Italian", "native_name": "Italiano", "voice_supported": True},
    {"code": "pt", "name": "Portuguese", "native_name": "Português", "voice_supported": True},
    {"code": "ja", "name": "Japanese", "native_name": "日本語", "voice_supported": True},
    {"code": "ko", "name": "Korean", "native_name": "한국어", "voice_supported": True},
    {"code": "zh", "name": "Chinese (Simplified)", "native_name": "简体中文", "voice_supported": True},
    {"code": "hi", "name": "Hindi", "native_name": "हिन्दी", "voice_supported": True},
    {"code": "ar", "name": "Arabic", "native_name": "العربية", "voice_supported": True},
    {"code": "ru", "name": "Russian", "native_name": "Русский", "voice_supported": True},
    {"code": "nl", "name": "Dutch", "native_name": "Nederlands", "voice_supported": True},
    {"code": "pl", "name": "Polish", "native_name": "Polski", "voice_supported": True},
    {"code": "tr", "name": "Turkish", "native_name": "Türkçe", "voice_supported": True},
    {"code": "vi", "name": "Vietnamese", "native_name": "Tiếng Việt", "voice_supported": True},
    {"code": "th", "name": "Thai", "native_name": "ไทย", "voice_supported": True},
    {"code": "id", "name": "Indonesian", "native_name": "Bahasa Indonesia", "voice_supported": True},
    {"code": "sv", "name": "Swedish", "native_name": "Svenska", "voice_supported": True},
    {"code": "da", "name": "Danish", "native_name": "Dansk", "voice_supported": True},
    {"code": "no", "name": "Norwegian", "native_name": "Norsk", "voice_supported": True},
    {"code": "fi", "name": "Finnish", "native_name": "Suomi", "voice_supported": True},
    {"code": "el", "name": "Greek", "native_name": "Ελληνικά", "voice_supported": True},
    {"code": "he", "name": "Hebrew", "native_name": "עברית", "voice_supported": True},
    {"code": "cs", "name": "Czech", "native_name": "Čeština", "voice_supported": True},
    {"code": "uk", "name": "Ukrainian", "native_name": "Українська", "voice_supported": True},
    {"code": "bn", "name": "Bengali", "native_name": "বাংলা", "voice_supported": True},
    {"code": "ta", "name": "Tamil", "native_name": "தமிழ்", "voice_supported": True},
    {"code": "te", "name": "Telugu", "native_name": "తెలుగు", "voice_supported": True},
    {"code": "mr", "name": "Marathi", "native_name": "मराठी", "voice_supported": True},

    # Text-Ready Languages
    {"code": "ur", "name": "Urdu", "native_name": "اردو", "voice_supported": False},
    {"code": "fa", "name": "Persian", "native_name": "فارسی", "voice_supported": False},
    {"code": "ro", "name": "Romanian", "native_name": "Română", "voice_supported": False},
    {"code": "hu", "name": "Hungarian", "native_name": "Magyar", "voice_supported": False},
    {"code": "sk", "name": "Slovak", "native_name": "Slovenčina", "voice_supported": False},
    {"code": "bg", "name": "Bulgarian", "native_name": "Български", "voice_supported": False},
    {"code": "hr", "name": "Croatian", "native_name": "Hrvatski", "voice_supported": False},
    {"code": "sr", "name": "Serbian", "native_name": "Српски", "voice_supported": False},
    {"code": "sl", "name": "Slovenian", "native_name": "Slovenščina", "voice_supported": False},
    {"code": "lt", "name": "Lithuanian", "native_name": "Lietuvių", "voice_supported": False},
    {"code": "lv", "name": "Latvian", "native_name": "Latviešu", "voice_supported": False},
    {"code": "et", "name": "Estonian", "native_name": "Eesti", "voice_supported": False},
    {"code": "ms", "name": "Malay", "native_name": "Bahasa Melayu", "voice_supported": False},
    {"code": "tl", "name": "Tagalog / Filipino", "native_name": "Tagalog", "voice_supported": False},
    {"code": "sw", "name": "Swahili", "native_name": "Kiswahili", "voice_supported": False},
    {"code": "af", "name": "Afrikaans", "native_name": "Afrikaans", "voice_supported": False},
    {"code": "is", "name": "Icelandic", "native_name": "Íslenska", "voice_supported": False},
    {"code": "ga", "name": "Irish", "native_name": "Gaeilge", "voice_supported": False},
    {"code": "cy", "name": "Welsh", "native_name": "Cymraeg", "voice_supported": False},
    {"code": "eu", "name": "Basque", "native_name": "Euskara", "voice_supported": False},
    {"code": "gl", "name": "Galician", "native_name": "Galego", "voice_supported": False},
    {"code": "ca", "name": "Catalan", "native_name": "Català", "voice_supported": False},
    {"code": "ml", "name": "Malayalam", "native_name": "മലയാളം", "voice_supported": False},
    {"code": "kn", "name": "Kannada", "native_name": "ಕನ್ನಡ", "voice_supported": False},
    {"code": "gu", "name": "Gujarati", "native_name": "ગુજરાતી", "voice_supported": False},
    {"code": "pa", "name": "Punjabi", "native_name": "ਪੰਜਾਬੀ", "voice_supported": False},
]

GEMINI_LANGUAGES = SUPPORTED_LANGUAGES

def get_supported_languages(capability: str = "all") -> List[Dict[str, Any]]:
    """Returns languages filtered by capability ('all' or 'voice')."""
    if (capability or "all").lower().strip() == "voice":
        return [l for l in SUPPORTED_LANGUAGES if l.get("voice_supported")]
    return SUPPORTED_LANGUAGES

def get_language_by_code(code: str) -> Optional[Dict[str, Any]]:
    """Finds a language dictionary by code or None."""
    if not code:
        return None
    code_lower = code.lower().strip()
    for l in SUPPORTED_LANGUAGES:
        if l["code"].lower() == code_lower:
            return l
    return None

def get_voice_supported_languages() -> List[Dict[str, Any]]:
    """Returns list of voice-supported languages."""
    return get_supported_languages(capability="voice")
