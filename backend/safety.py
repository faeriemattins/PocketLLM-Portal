import re

class SafetyFilter:
    def __init__(self):
        self.profanity_list = {
            "damn", "hell", "crap", "idiot", "stupid"
        }
        # Basic PII regex patterns
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')

    def check(self, text: str) -> tuple[bool, str, str]:
        """
        Checks text for safety violations.
        Returns: (is_safe, reason, sanitized_text)
        """
        # Normalize text for checking
        text_lower = text.lower()
        
        # Check profanity
        words = text_lower.split()
        for word in words:
            # Remove common punctuation from word
            clean_word = word.strip('.,!?;:"\'-')
            if clean_word in self.profanity_list:
                return False, f"Profanity detected: '{word}'", text

        # Check PII (use original text for regex)
        if self.email_pattern.search(text):
            return False, "PII (Email) detected", text
        
        if self.phone_pattern.search(text):
            return False, "PII (Phone) detected", text

        return True, "", text

safety_filter = SafetyFilter()
