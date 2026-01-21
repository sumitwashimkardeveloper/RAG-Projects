"""
Text Preprocessing and Cleaning
"""

import re
import unicodedata
import logging
from typing import List

logger = logging.getLogger(__name__)


class TextCleaner:
    """
    Clean and normalize text from various sources
    Handles special characters, whitespace, formatting, etc.
    """

    @staticmethod
    def clean(text: str, remove_urls: bool = False, remove_emails: bool = False) -> str:
        """
        Comprehensive text cleaning

        Args:
            text: Raw text to clean
            remove_urls: Remove URLs
            remove_emails: Remove email addresses

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        text = TextCleaner.normalize_unicode(text)
        text = TextCleaner.remove_extra_whitespace(text)
        text = TextCleaner.remove_control_characters(text)
        text = TextCleaner.fix_common_encoding_issues(text)

        if remove_urls:
            text = TextCleaner.remove_urls(text)

        if remove_emails:
            text = TextCleaner.remove_emails(text)

        return text.strip()

    @staticmethod
    def normalize_unicode(text: str) -> str:
        """Normalize unicode characters"""
        return unicodedata.normalize("NFKD", text)

    @staticmethod
    def remove_extra_whitespace(text: str) -> str:
        """Remove extra spaces, tabs, and newlines"""
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\n\s*\n", "\n\n", text)
        return text

    @staticmethod
    def remove_control_characters(text: str) -> str:
        """Remove control characters and non-printable chars"""
        return "".join(
            char
            for char in text
            if unicodedata.category(char)[0] != "C" or char in "\n\r\t"
        )

    @staticmethod
    def fix_common_encoding_issues(text: str) -> str:
        """Fix common encoding problems"""
        replacements = {
            "‘": "'",  # Left single quote
            "’": "'",  # Right single quote
            "“": '"',  # Left double quote
            "”": '"',  # Right double quote
            "–": "-",  # En dash
            "—": "-",  # Em dash
            "…": "...",  # Ellipsis
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        return text

    @staticmethod
    def remove_urls(text: str) -> str:
        """Remove URLs from text"""
        url_pattern = r"https?://\S+|www\.\S+"
        return re.sub(url_pattern, "", text)

    @staticmethod
    def remove_emails(text: str) -> str:
        """Remove email addresses from text"""
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        return re.sub(email_pattern, "", text)

    @staticmethod
    def remove_html_tags(text: str) -> str:
        """Remove HTML tags"""
        return re.sub(r"<[^>]+>", "", text)

    @staticmethod
    def remove_markdown_formatting(text: str) -> str:
        """Remove markdown formatting while preserving text"""
        text = re.sub(r"#+\s+", "", text)  # Headers
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)  # Bold
        text = re.sub(r"\*(.+?)\*", r"\1", text)  # Italic
        text = re.sub(r"__(.+?)__", r"\1", text)  # Bold (alt)
        text = re.sub(r"_(.+?)_", r"\1", text)  # Italic (alt)
        text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)  # Links
        text = re.sub(r"`(.+?)`", r"\1", text)  # Inline code
        return text

    @staticmethod
    def remove_special_characters(text: str, keep_punctuation: bool = True) -> str:
        """
        Remove special characters

        Args:
            text: Text to clean
            keep_punctuation: Keep basic punctuation

        Returns:
            Cleaned text
        """
        if keep_punctuation:
            pattern = r"[^a-zA-Z0-9\s.!?,;\-]"
        else:
            pattern = r"[^a-zA-Z0-9\s]"

        return re.sub(pattern, "", text)

    @staticmethod
    def remove_numbers(text: str) -> str:
        """Remove all numeric characters"""
        return re.sub(r"\d+", "", text)

    @staticmethod
    def lowercase(text: str) -> str:
        """Convert to lowercase"""
        return text.lower()

    @staticmethod
    def remove_duplicate_lines(text: str) -> str:
        """Remove duplicate consecutive lines"""
        lines = text.split("\n")
        unique_lines = []
        prev_line = ""

        for line in lines:
            if line.strip() != prev_line.strip():
                unique_lines.append(line)
                prev_line = line

        return "\n".join(unique_lines)

    @staticmethod
    def remove_stopwords(text: str, language: str = "english") -> str:
        """
        Remove common stopwords

        Args:
            text: Text to process
            language: Language for stopwords

        Returns:
            Text without stopwords
        """
        try:
            import nltk
            from nltk.corpus import stopwords

            try:
                nltk.data.find("corpora/stopwords")
            except LookupError:
                nltk.download("stopwords")

            stop_words = set(stopwords.words(language))
            words = text.split()
            filtered = [w for w in words if w.lower() not in stop_words]
            return " ".join(filtered)
        except Exception as e:
            logger.warning(f"Failed to remove stopwords: {str(e)}")
            return text
