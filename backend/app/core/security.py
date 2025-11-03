"""
Security utilities: password hashing, JWT tokens, RUT validation
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt
from jose import JWTError, jwt
import re

# JWT Configuration (importar desde config en producción)
SECRET_KEY = "dev-jwt-secret-key-change-in-production"  # TODO: Move to env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30


# ==================== PASSWORD HASHING ====================

def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt directly.
    bcrypt has a 72-byte limit, so truncate if necessary.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    # bcrypt has 72-byte limit, truncate manually
    password_bytes = password.encode('utf-8')[:72]
    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash using bcrypt directly.
    bcrypt has a 72-byte limit, so truncate if necessary.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    # bcrypt has 72-byte limit, truncate manually
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# ==================== JWT TOKENS ====================

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Payload data (user_id, email, tipo_cliente)
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: str) -> str:
    """
    Create JWT refresh token (longer expiration).
    
    Args:
        user_id: User ID to encode in token
        
    Returns:
        Encoded refresh token string
    """
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        "user_id": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload dict
        
    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")


# ==================== RUT VALIDATION (CHILE) ====================

def clean_rut(rut: str) -> str:
    """
    Clean RUT removing dots and hyphens.
    
    Args:
        rut: RUT string (e.g., "12.345.678-5")
        
    Returns:
        Cleaned RUT (e.g., "123456785")
    """
    return rut.replace(".", "").replace("-", "").strip().upper()


def validate_rut(rut: str) -> bool:
    """
    Validate Chilean RUT using módulo 11 algorithm.
    
    Args:
        rut: RUT string (e.g., "12.345.678-5" or "123456785")
        
    Returns:
        True if valid, False otherwise
        
    Example:
        >>> validate_rut("12.345.678-5")
        True
        >>> validate_rut("12.345.678-9")
        False
    """
    try:
        # Clean RUT
        rut_clean = clean_rut(rut)
        
        # Must have at least 2 characters (number + check digit)
        if len(rut_clean) < 2:
            return False
        
        # Separate body and check digit
        rut_body = rut_clean[:-1]
        check_digit = rut_clean[-1]
        
        # Body must be numeric
        if not rut_body.isdigit():
            return False
        
        # Calculate expected check digit
        suma = 0
        multiplicador = 2
        
        for digit in reversed(rut_body):
            suma += int(digit) * multiplicador
            multiplicador += 1
            if multiplicador > 7:
                multiplicador = 2
        
        resto = suma % 11
        esperado = 11 - resto
        
        # Convert to check digit character
        if esperado == 11:
            esperado_str = "0"
        elif esperado == 10:
            esperado_str = "K"
        else:
            esperado_str = str(esperado)
        
        # Compare
        return check_digit == esperado_str
        
    except Exception:
        return False


def detect_tipo_cliente_from_rut(rut: str) -> str:
    """
    Detect customer type (persona/empresa) from RUT.
    
    Chilean RUTs starting with 7x or 8x are typically companies.
    Others are typically natural persons.
    
    Args:
        rut: RUT string
        
    Returns:
        "empresa" or "persona"
        
    Note: This is a heuristic and may not be 100% accurate.
    """
    try:
        rut_clean = clean_rut(rut)
        first_digit = int(rut_clean[0])
        
        # RUTs starting with 7 or 8 are usually companies
        if first_digit in [7, 8]:
            return "empresa"
        else:
            return "persona"
    except Exception:
        return "persona"  # Default to persona if error


def format_rut(rut: str) -> str:
    """
    Format RUT with dots and hyphen.
    
    Args:
        rut: RUT string (cleaned or unformatted)
        
    Returns:
        Formatted RUT (e.g., "12.345.678-5")
        
    Example:
        >>> format_rut("123456785")
        "12.345.678-5"
    """
    rut_clean = clean_rut(rut)
    
    if len(rut_clean) < 2:
        return rut_clean
    
    body = rut_clean[:-1]
    check_digit = rut_clean[-1]
    
    # Add dots every 3 digits from right to left
    formatted_body = ""
    for i, digit in enumerate(reversed(body)):
        if i > 0 and i % 3 == 0:
            formatted_body = "." + formatted_body
        formatted_body = digit + formatted_body
    
    return f"{formatted_body}-{check_digit}"


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    # Test password hashing
    password = "SecurePass123!"
    hashed = get_password_hash(password)
    print(f"Hashed: {hashed}")
    print(f"Verify: {verify_password(password, hashed)}")
    
    # Test JWT tokens
    token = create_access_token({"user_id": "123", "email": "test@example.com"})
    print(f"\nToken: {token}")
    decoded = decode_token(token)
    print(f"Decoded: {decoded}")
    
    # Test RUT validation
    test_ruts = [
        "12.345.678-5",  # Valid persona
        "76.123.456-K",  # Valid empresa
        "12.345.678-9",  # Invalid check digit
        "123456785",     # Valid (no format)
    ]
    
    print("\nRUT Validation:")
    for rut in test_ruts:
        is_valid = validate_rut(rut)
        tipo = detect_tipo_cliente_from_rut(rut)
        formatted = format_rut(rut)
        print(f"{rut:20} -> Valid: {is_valid:5} | Tipo: {tipo:7} | Formatted: {formatted}")
