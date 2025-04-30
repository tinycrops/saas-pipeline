"""
Text Utilities

This module provides functions for text processing and analysis,
particularly focused on operations relevant to AI and NLP tasks.
"""

import re
import logging
from typing import List, Dict, Optional, Union, Any, Tuple

# Attempt to import optional dependencies
try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

logger = logging.getLogger(__name__)

def clean_text(text: str, 
               remove_urls: bool = True,
               remove_html: bool = True,
               lowercase: bool = True,
               remove_extra_spaces: bool = True,
               remove_special_chars: bool = False) -> str:
    """
    Clean text by applying various transformations.
    
    Args:
        text: Text to clean
        remove_urls: Whether to remove URLs
        remove_html: Whether to remove HTML tags
        lowercase: Whether to convert to lowercase
        remove_extra_spaces: Whether to remove redundant whitespace
        remove_special_chars: Whether to remove special characters
        
    Returns:
        Cleaned text
    """
    # Handle None or empty string
    if not text:
        return ""
    
    result = text
    
    # Remove URLs
    if remove_urls:
        result = re.sub(r'https?://\S+|www\.\S+', '', result)
        
    # Remove HTML tags
    if remove_html:
        result = re.sub(r'<.*?>', '', result)
        
    # Convert to lowercase
    if lowercase:
        result = result.lower()
        
    # Remove special characters (keep alphanumeric, space, period)
    if remove_special_chars:
        result = re.sub(r'[^a-zA-Z0-9\s\.]', '', result)
        
    # Remove extra whitespace
    if remove_extra_spaces:
        result = re.sub(r'\s+', ' ', result).strip()
        
    return result

def chunk_text(text: str, 
               max_chunk_size: int = 2000, 
               overlap: int = 100, 
               respect_sentences: bool = True) -> List[str]:
    """
    Split text into overlapping chunks of a maximum size.
    
    Args:
        text: Text to split
        max_chunk_size: Maximum size of each chunk (in characters)
        overlap: Number of characters to overlap between chunks
        respect_sentences: Try to break at sentence boundaries
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
        
    # If chunk size is larger than text, return the whole text
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    
    # Try to respect sentence boundaries if requested
    if respect_sentences and NLTK_AVAILABLE:
        try:
            # Download nltk data if not already downloaded
            try:
                sent_tokenize("Test.")
            except LookupError:
                nltk.download('punkt', quiet=True)
                
            sentences = sent_tokenize(text)
            current_chunk = ""
            
            for sentence in sentences:
                # If adding this sentence would exceed max size
                if len(current_chunk) + len(sentence) > max_chunk_size:
                    # Add the current chunk to the list
                    if current_chunk:
                        chunks.append(current_chunk)
                    
                    # Start a new chunk with this sentence
                    current_chunk = sentence
                else:
                    # Add this sentence to the current chunk
                    if current_chunk:
                        current_chunk += " " + sentence
                    else:
                        current_chunk = sentence
            
            # Add the last chunk if it exists
            if current_chunk:
                chunks.append(current_chunk)
                
        except Exception as e:
            logger.warning(f"Error chunking by sentences: {str(e)}. Falling back to character chunking.")
            # Fall back to non-sentence-aware chunking
            respect_sentences = False
    
    # If we're not respecting sentences or NLTK isn't available
    if not respect_sentences or not NLTK_AVAILABLE:
        start = 0
        while start < len(text):
            end = start + max_chunk_size
            
            # If we're not at the end, try to break at a space
            if end < len(text):
                # Try to find a space to break at
                space_pos = text.rfind(' ', start, end)
                if space_pos != -1:
                    end = space_pos
            
            # Add the chunk
            chunks.append(text[start:end].strip())
            
            # Move to the next chunk, accounting for overlap
            start = end - overlap if end > overlap else end
    
    return chunks

def extract_keywords(text: str, 
                     max_keywords: int = 10, 
                     min_word_length: int = 3) -> List[str]:
    """
    Extract important keywords from text.
    
    Args:
        text: Text to analyze
        max_keywords: Maximum number of keywords to return
        min_word_length: Minimum length of words to consider
        
    Returns:
        List of keywords
    """
    if not NLTK_AVAILABLE:
        logger.warning("NLTK not available. Install nltk for keyword extraction.")
        words = re.findall(r'\b\w+\b', text.lower())
        word_counts = {}
        for word in words:
            if len(word) >= min_word_length:
                word_counts[word] = word_counts.get(word, 0) + 1
        return [w for w, _ in sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:max_keywords]]
    
    try:
        # Download needed NLTK data if not already downloaded
        try:
            word_tokenize("Test.")
            stopwords.words('english')
        except LookupError:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
        
        # Tokenize and filter words
        stop_words = set(stopwords.words('english'))
        words = word_tokenize(text.lower())
        
        # Filter out stopwords and short words
        filtered_words = [
            word for word in words 
            if word.isalpha() and 
            word not in stop_words and 
            len(word) >= min_word_length
        ]
        
        # Count word frequencies
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
            
        # Get the most common words
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in keywords[:max_keywords]]
        
    except Exception as e:
        logger.error(f"Error extracting keywords: {str(e)}")
        return []

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Count the number of tokens in a text string using tiktoken.
    
    Args:
        text: Text to count tokens for
        model: Model name to determine tokenization (e.g., 'gpt-4', 'gpt-3.5-turbo')
        
    Returns:
        Number of tokens
    """
    if not TIKTOKEN_AVAILABLE:
        # Fallback token estimation (very approximate)
        logger.warning("tiktoken not available, using approximate token count.")
        return len(text.split()) * 4 // 3  # Rough estimate
    
    try:
        # Get the encoding for the specified model
        encoding = tiktoken.encoding_for_model(model)
        
        # Count tokens
        tokens = encoding.encode(text)
        return len(tokens)
        
    except Exception as e:
        logger.warning(f"Error counting tokens with tiktoken: {str(e)}. Using fallback method.")
        # Fallback token estimation
        return len(text.split()) * 4 // 3  # Rough estimate

def summarize_text(text: str, max_length: int = 200) -> str:
    """
    Generate a simple extractive summary of the text by selecting important sentences.
    This is a basic approach and doesn't use ML models.
    
    Args:
        text: Text to summarize
        max_length: Approximate maximum length of summary in characters
        
    Returns:
        Summarized text
    """
    if not NLTK_AVAILABLE:
        logger.warning("NLTK not available. Install nltk for better summarization.")
        # Simple fallback - just return the first part of the text
        return text[:max_length].rsplit('.', 1)[0] + '.' if len(text) > max_length else text
    
    try:
        # Download needed NLTK data if not already downloaded
        try:
            sent_tokenize("Test.")
            stopwords.words('english')
        except LookupError:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
        
        # Tokenize sentences
        sentences = sent_tokenize(text)
        
        # If we only have a few sentences, return all of them
        if len(''.join(sentences)) <= max_length or len(sentences) <= 3:
            return text
            
        # Calculate sentence scores based on word frequency
        stop_words = set(stopwords.words('english'))
        word_frequencies = {}
        
        # Count word frequencies excluding stopwords
        for sentence in sentences:
            for word in word_tokenize(sentence.lower()):
                if word.isalpha() and word not in stop_words:
                    word_frequencies[word] = word_frequencies.get(word, 0) + 1
        
        # Normalize word frequencies
        max_frequency = max(word_frequencies.values()) if word_frequencies else 1
        normalized_frequencies = {
            word: freq / max_frequency 
            for word, freq in word_frequencies.items()
        }
        
        # Score each sentence
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            score = 0
            for word in word_tokenize(sentence.lower()):
                if word in normalized_frequencies:
                    score += normalized_frequencies[word]
            
            # Add positional bias for first few sentences
            if i == 0:
                score *= 1.5
            elif i == 1:
                score *= 1.2
                
            sentence_scores[sentence] = score
        
        # Select top sentences
        summary_sentences = []
        summary_length = 0
        
        for sentence, _ in sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True):
            if summary_length + len(sentence) <= max_length:
                summary_sentences.append(sentence)
                summary_length += len(sentence)
            else:
                break
        
        # If we couldn't add any sentences, at least add the highest-scoring one
        if not summary_sentences and sentences:
            highest_scoring = max(sentence_scores.items(), key=lambda x: x[1])[0]
            summary_sentences = [highest_scoring]
        
        # Reorder sentences to match the original order
        original_order_summary = [sent for sent in sentences if sent in summary_sentences]
        
        return ' '.join(original_order_summary)
        
    except Exception as e:
        logger.error(f"Error summarizing text: {str(e)}")
        # Fallback to simple approach
        return text[:max_length].rsplit('.', 1)[0] + '.' if len(text) > max_length else text

def similarity_score(text1: str, text2: str) -> float:
    """
    Calculate a simple similarity score between two text strings.
    This uses a basic approach and not advanced ML models like embeddings.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score between 0.0 and 1.0
    """
    if not text1 or not text2:
        return 0.0
    
    if not NLTK_AVAILABLE:
        logger.warning("NLTK not available. Install nltk for better text similarity.")
        # Simple fallback using set comparison of words
        words1 = set(re.findall(r'\b\w+\b', text1.lower()))
        words2 = set(re.findall(r'\b\w+\b', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
            
        # Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    try:
        # Download needed NLTK data if not already downloaded
        try:
            word_tokenize("Test.")
            stopwords.words('english')
        except LookupError:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
        
        # Tokenize and process
        stop_words = set(stopwords.words('english'))
        
        # Process each text to get filtered token lists
        def process_text(text):
            tokens = word_tokenize(text.lower())
            return [word for word in tokens if word.isalpha() and word not in stop_words]
            
        tokens1 = process_text(text1)
        tokens2 = process_text(text2)
        
        # Calculate term frequency dictionaries
        def get_tf(tokens):
            tf_dict = {}
            for token in tokens:
                tf_dict[token] = tf_dict.get(token, 0) + 1
            return tf_dict
            
        tf1 = get_tf(tokens1)
        tf2 = get_tf(tokens2)
        
        # Find common terms
        common_tokens = set(tf1.keys()).intersection(set(tf2.keys()))
        
        # Calculate similarity using cosine similarity
        if not common_tokens:
            return 0.0
            
        # Dot product
        dot_product = sum(tf1[token] * tf2[token] for token in common_tokens)
        
        # Magnitudes
        magnitude1 = sum(tf1[token]**2 for token in tf1)
        magnitude2 = sum(tf2[token]**2 for token in tf2)
        
        # Cosine similarity
        similarity = dot_product / ((magnitude1 * magnitude2)**0.5) if magnitude1 > 0 and magnitude2 > 0 else 0.0
        
        return max(0.0, min(1.0, similarity))  # Clamp to [0, 1]
        
    except Exception as e:
        logger.error(f"Error calculating similarity: {str(e)}")
        return 0.0 