"""
Test script for authentication system
Run: python -m backend.scripts.test_auth
"""

import asyncio
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_token,
    validate_rut,
    detect_tipo_cliente_from_rut,
    format_rut
)

async def test_password_hashing():
    """Test password hashing and verification."""
    print("\n" + "="*60)
    print("TEST 1: Password Hashing")
    print("="*60)
    
    password = "SecurePass123!"
    hashed = get_password_hash(password)
    
    print(f"Password: {password}")
    print(f"Hashed: {hashed[:50]}...")
    print(f"Verify correct password: {verify_password(password, hashed)}")
    print(f"Verify wrong password: {verify_password('WrongPass', hashed)}")
    
    assert verify_password(password, hashed), "Password verification failed!"
    print("✅ Password hashing works!")


async def test_jwt_tokens():
    """Test JWT token creation and decoding."""
    print("\n" + "="*60)
    print("TEST 2: JWT Tokens")
    print("="*60)
    
    token_data = {
        "user_id": "test-user-123",
        "email": "test@example.com",
        "tipo_cliente": "persona"
    }
    
    token = create_access_token(token_data)
    print(f"Token created: {token[:50]}...")
    
    decoded = decode_token(token)
    print(f"Decoded user_id: {decoded.get('user_id')}")
    print(f"Decoded email: {decoded.get('email')}")
    print(f"Decoded tipo_cliente: {decoded.get('tipo_cliente')}")
    
    assert decoded.get('user_id') == token_data['user_id'], "Token decode failed!"
    print("✅ JWT tokens work!")


async def test_rut_validation():
    """Test Chilean RUT validation."""
    print("\n" + "="*60)
    print("TEST 3: RUT Validation")
    print("="*60)
    
    test_ruts = [
        ("12.345.678-5", True, "persona"),   # Valid persona
        ("76.123.456-K", True, "empresa"),   # Valid empresa
        ("12.345.678-9", False, "persona"),  # Invalid check digit
        ("123456785", True, "persona"),      # Valid (no format)
        ("87.654.321-2", True, "empresa"),   # Valid empresa
    ]
    
    print(f"{'RUT':<20} {'Valid':<8} {'Tipo':<10} {'Formatted'}")
    print("-" * 60)
    
    for rut, expected_valid, expected_tipo in test_ruts:
        is_valid = validate_rut(rut)
        tipo = detect_tipo_cliente_from_rut(rut)
        formatted = format_rut(rut)
        
        status = "✅" if is_valid == expected_valid else "❌"
        print(f"{rut:<20} {str(is_valid):<8} {tipo:<10} {formatted} {status}")
        
        assert is_valid == expected_valid, f"RUT validation failed for {rut}"
        assert tipo == expected_tipo, f"Tipo detection failed for {rut}"
    
    print("✅ RUT validation works!")


async def test_full_registration_flow():
    """Simulate a full registration flow."""
    print("\n" + "="*60)
    print("TEST 4: Full Registration Flow Simulation")
    print("="*60)
    
    # Step 1: User enters RUT
    rut = "12.345.678-5"
    print(f"\n1. User enters RUT: {rut}")
    
    # Step 2: Validate RUT
    is_valid = validate_rut(rut)
    print(f"   RUT valid: {is_valid}")
    
    if not is_valid:
        print("   ❌ Registration would fail here")
        return
    
    # Step 3: Auto-detect tipo_cliente
    tipo_cliente = detect_tipo_cliente_from_rut(rut)
    print(f"   Auto-detected tipo_cliente: {tipo_cliente}")
    
    # Step 4: User completes registration
    user_data = {
        "email": "juan.perez@example.com",
        "password": "SecurePass123!",
        "nombre": "Juan",
        "apellido": "Pérez",
        "rut": rut,
        "tipo_cliente": tipo_cliente,
        "region": "Metropolitana",
    }
    
    print(f"\n2. User completes registration:")
    for key, value in user_data.items():
        if key != "password":
            print(f"   {key}: {value}")
    
    # Step 5: Hash password
    hashed_password = get_password_hash(user_data["password"])
    print(f"\n3. Password hashed: {hashed_password[:40]}...")
    
    # Step 6: Create JWT token (simulating successful registration)
    token = create_access_token({
        "user_id": "generated-uuid-here",
        "email": user_data["email"],
        "tipo_cliente": user_data["tipo_cliente"]
    })
    print(f"\n4. JWT token created: {token[:50]}...")
    
    # Step 7: Verify token can be decoded
    decoded = decode_token(token)
    print(f"\n5. Token decoded successfully:")
    print(f"   user_id: {decoded.get('user_id')}")
    print(f"   email: {decoded.get('email')}")
    print(f"   tipo_cliente: {decoded.get('tipo_cliente')}")
    
    print("\n✅ Full registration flow simulation successful!")


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("TESTING AUTHENTICATION SYSTEM")
    print("="*60)
    
    try:
        await test_password_hashing()
        await test_jwt_tokens()
        await test_rut_validation()
        await test_full_registration_flow()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED! ✅")
        print("="*60)
        print("\nAuthentication system is ready to use!")
        print("Next steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start FastAPI server: uvicorn app.main:app --reload")
        print("3. Test endpoints at http://localhost:8000/docs")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
