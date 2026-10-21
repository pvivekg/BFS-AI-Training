"""Data encryption for PII (Personally Identifiable Information)."""

import os
import json
from typing import Any, Dict
from cryptography.fernet import Fernet, InvalidToken

# Encryption configuration
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())


class DataEncryption:
    """Encrypt and decrypt sensitive data."""

    # Fields that should be encrypted (PII)
    PII_FIELDS = {
        "applicant_id",
        "income",
        "credit_score",
        "existing_liabilities",
    }

    def __init__(self, key: str = None):
        """Initialize encryption with key.

        Args:
            key: Fernet encryption key (generates new if not provided)
        """
        try:
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        except Exception:
            # Generate new key if invalid
            new_key = Fernet.generate_key()
            self.cipher = Fernet(new_key)
            print(f"Generated new encryption key: {new_key.decode()}")
            print("Set ENCRYPTION_KEY environment variable to this value")

    def encrypt_pii(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt PII fields in data.

        Args:
            data: Dictionary with data to encrypt

        Returns:
            Dictionary with PII fields encrypted
        """
        encrypted_data = data.copy()

        for field in self.PII_FIELDS:
            if field in encrypted_data and encrypted_data[field] is not None:
                try:
                    # Convert to string for encryption
                    value_str = str(encrypted_data[field])
                    # Encrypt
                    encrypted_value = self.cipher.encrypt(value_str.encode())
                    # Store as string (for JSON serialization)
                    encrypted_data[field] = encrypted_value.decode()
                except Exception as e:
                    print(f"Error encrypting {field}: {e}")

        return encrypted_data

    def decrypt_pii(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt PII fields in data.

        Args:
            data: Dictionary with encrypted data

        Returns:
            Dictionary with PII fields decrypted
        """
        decrypted_data = data.copy()

        for field in self.PII_FIELDS:
            if field in decrypted_data and decrypted_data[field] is not None:
                try:
                    # Convert from string to bytes
                    encrypted_value = decrypted_data[field].encode()
                    # Decrypt
                    decrypted_value = self.cipher.decrypt(encrypted_value)
                    # Try to convert back to original type
                    decrypted_str = decrypted_value.decode()

                    # Try to convert to number if applicable
                    if field in ["income", "credit_score", "existing_liabilities"]:
                        try:
                            decrypted_data[field] = float(decrypted_str)
                        except ValueError:
                            decrypted_data[field] = decrypted_str
                    else:
                        decrypted_data[field] = decrypted_str

                except InvalidToken:
                    print(f"Invalid token for field {field}")
                except Exception as e:
                    print(f"Error decrypting {field}: {e}")

        return decrypted_data

    def encrypt_dict(self, data: Dict[str, Any]) -> str:
        """Encrypt entire dictionary to JSON string.

        Args:
            data: Dictionary to encrypt

        Returns:
            Encrypted JSON string
        """
        try:
            json_str = json.dumps(data)
            encrypted = self.cipher.encrypt(json_str.encode())
            return encrypted.decode()
        except Exception as e:
            print(f"Error encrypting dict: {e}")
            return ""

    def decrypt_dict(self, encrypted_str: str) -> Dict[str, Any]:
        """Decrypt dictionary from encrypted JSON string.

        Args:
            encrypted_str: Encrypted JSON string

        Returns:
            Decrypted dictionary
        """
        try:
            encrypted_bytes = encrypted_str.encode()
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return json.loads(decrypted.decode())
        except InvalidToken:
            print("Invalid encryption token")
            return {}
        except Exception as e:
            print(f"Error decrypting dict: {e}")
            return {}


# Global encryption instance
encryptor = DataEncryption(ENCRYPTION_KEY)


def encrypt_application_data(app_data: Dict[str, Any]) -> Dict[str, Any]:
    """Encrypt application data for storage.

    Args:
        app_data: Application data dictionary

    Returns:
        Encrypted application data
    """
    return encryptor.encrypt_pii(app_data)


def decrypt_application_data(encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
    """Decrypt application data for processing.

    Args:
        encrypted_data: Encrypted application data

    Returns:
        Decrypted application data
    """
    return encryptor.decrypt_pii(encrypted_data)


# Test encryption
if __name__ == "__main__":
    # Test data
    test_data = {
        "applicant_id": "APP001",
        "age": 35,
        "income": 75000,
        "employment_type": "employed",
        "credit_score": 720,
        "loan_amount": 250000,
        "existing_liabilities": 50000,
    }

    print("Original data:")
    print(test_data)

    # Encrypt
    encrypted = encryptor.encrypt_pii(test_data)
    print("\nEncrypted data:")
    print(encrypted)

    # Decrypt
    decrypted = encryptor.decrypt_pii(encrypted)
    print("\nDecrypted data:")
    print(decrypted)

    # Verify
    print("\nVerification:")
    print(f"applicant_id matches: {decrypted['applicant_id'] == test_data['applicant_id']}")
    print(f"income matches: {decrypted['income'] == test_data['income']}")
    print(f"credit_score matches: {decrypted['credit_score'] == test_data['credit_score']}")
