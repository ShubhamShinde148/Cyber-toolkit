"""
Hash Generator Tool
Generates MD5, SHA1, SHA256, SHA512 hashes from input text or files.
"""

import hashlib
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class HashResult:
    """Result of hash generation."""
    input_text: str
    md5: str
    sha1: str
    sha256: str
    sha512: str
    algorithm: Optional[str] = None
    single_hash: Optional[str] = None


class HashTool:
    """Generate various cryptographic hashes."""
    
    SUPPORTED_ALGORITHMS = ['md5', 'sha1', 'sha256', 'sha512', 'sha384', 'sha224']
    
    def __init__(self):
        pass
    
    def generate_all(self, text: str) -> HashResult:
        """
        Generate all supported hashes for the given text.
        
        Args:
            text: Input text to hash
            
        Returns:
            HashResult containing all hash values
        """
        text_bytes = text.encode('utf-8')
        
        return HashResult(
            input_text=text[:50] + '...' if len(text) > 50 else text,
            md5=hashlib.md5(text_bytes).hexdigest(),
            sha1=hashlib.sha1(text_bytes).hexdigest(),
            sha256=hashlib.sha256(text_bytes).hexdigest(),
            sha512=hashlib.sha512(text_bytes).hexdigest()
        )
    
    def generate(self, text: str, algorithm: str = 'sha256') -> HashResult:
        """
        Generate a specific hash for the given text.
        
        Args:
            text: Input text to hash
            algorithm: Hash algorithm (md5, sha1, sha256, sha512)
            
        Returns:
            HashResult with the specific hash
        """
        algorithm = algorithm.lower()
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}. Supported: {self.SUPPORTED_ALGORITHMS}")
        
        text_bytes = text.encode('utf-8')
        hash_func = getattr(hashlib, algorithm)
        hash_value = hash_func(text_bytes).hexdigest()
        
        all_hashes = self.generate_all(text)
        all_hashes.algorithm = algorithm
        all_hashes.single_hash = hash_value
        
        return all_hashes
    
    def verify_hash(self, text: str, hash_value: str, algorithm: str = None) -> Dict:
        """
        Verify if a given hash matches the text.
        
        Args:
            text: Original text
            hash_value: Hash to verify
            algorithm: Optional specific algorithm to check
            
        Returns:
            Dict with verification results
        """
        text_bytes = text.encode('utf-8')
        hash_value = hash_value.lower().strip()
        
        results = {
            'match': False,
            'algorithm': None,
            'checked_algorithms': []
        }
        
        algorithms_to_check = [algorithm] if algorithm else self.SUPPORTED_ALGORITHMS
        
        for algo in algorithms_to_check:
            if algo not in self.SUPPORTED_ALGORITHMS:
                continue
                
            hash_func = getattr(hashlib, algo)
            computed = hash_func(text_bytes).hexdigest()
            results['checked_algorithms'].append(algo)
            
            if computed == hash_value:
                results['match'] = True
                results['algorithm'] = algo
                break
        
        return results
    
    def hash_file(self, file_content: bytes, algorithm: str = 'sha256') -> str:
        """
        Generate hash for file content.
        
        Args:
            file_content: Binary file content
            algorithm: Hash algorithm
            
        Returns:
            Hex digest of the hash
        """
        algorithm = algorithm.lower()
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        hash_func = getattr(hashlib, algorithm)
        return hash_func(file_content).hexdigest()


# Convenience functions
def generate_hash(text: str, algorithm: str = 'sha256') -> str:
    """Quick hash generation."""
    tool = HashTool()
    return tool.generate(text, algorithm).single_hash


def generate_all_hashes(text: str) -> Dict[str, str]:
    """Generate all common hashes."""
    tool = HashTool()
    result = tool.generate_all(text)
    return {
        'md5': result.md5,
        'sha1': result.sha1,
        'sha256': result.sha256,
        'sha512': result.sha512
    }
