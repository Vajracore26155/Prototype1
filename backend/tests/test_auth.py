"""
Unit Tests: Authentication & Authorization
Phase 8: Comprehensive test coverage
"""
import pytest
from datetime import datetime, timedelta
from jose import jwt

from app.auth.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    decode_access_token
)
from app.auth.permissions import Permission, has_permission


class TestPasswordHashing:
    """Test password hashing functions"""
    
    def test_password_hash(self):
        """Test password is hashed correctly"""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
    
    def test_verify_correct_password(self):
        """Test correct password verification"""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_incorrect_password(self):
        """Test incorrect password verification"""
        password = "SecurePassword123!"
        wrong_password = "WrongPassword123!"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False


class TestJWTTokens:
    """Test JWT token creation and verification"""
    
    def test_create_access_token(self):
        """Test JWT token creation"""
        data = {"sub": "user@example.com", "user_id": 1}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
    
    def test_decode_access_token(self):
        """Test JWT token decoding"""
        data = {"sub": "user@example.com", "user_id": 1}
        token = create_access_token(data)
        
        decoded = decode_access_token(token)
        
        assert decoded is not None
        assert decoded.get("sub") == "user@example.com"
        assert decoded.get("user_id") == 1
    
    def test_expired_token(self):
        """Test expired token is rejected"""
        data = {"sub": "user@example.com"}
        # Create token that expires immediately
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        decoded = decode_access_token(token)
        assert decoded is None
    
    def test_invalid_token(self):
        """Test invalid token is rejected"""
        invalid_token = "invalid.token.here"
        decoded = decode_access_token(invalid_token)
        
        assert decoded is None


class TestPermissions:
    """Test permission system"""
    
    def test_has_permission_with_permission(self):
        """Test user has required permission"""
        user_permissions = [Permission.AUDIT_READ, Permission.DEVICE_READ]
        
        assert has_permission(user_permissions, Permission.AUDIT_READ) is True
    
    def test_has_permission_without_permission(self):
        """Test user lacks required permission"""
        user_permissions = [Permission.DEVICE_READ]
        
        assert has_permission(user_permissions, Permission.AUDIT_READ) is False
    
    def test_admin_has_all_permissions(self):
        """Test ADMIN permission grants all access"""
        user_permissions = [Permission.ADMIN]
        
        assert has_permission(user_permissions, Permission.AUDIT_READ) is True
        assert has_permission(user_permissions, Permission.DEVICE_WRITE) is True
        assert has_permission(user_permissions, Permission.FINDING_WRITE) is True


@pytest.mark.asyncio
class TestAuthenticationFlow:
    """Test complete authentication flow"""
    
    async def test_login_success(self, test_client, test_user):
        """Test successful login"""
        response = test_client.post(
            "/api/auth/login",
            json={
                "username": test_user.email,
                "password": "TestPassword123!"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
    
    async def test_login_invalid_credentials(self, test_client, test_user):
        """Test login with invalid credentials"""
        response = test_client.post(
            "/api/auth/login",
            json={
                "username": test_user.email,
                "password": "WrongPassword"
            }
        )
        
        assert response.status_code == 401
    
    async def test_protected_endpoint_without_token(self, test_client):
        """Test accessing protected endpoint without token"""
        response = test_client.get("/api/devices")
        
        assert response.status_code == 401
    
    async def test_protected_endpoint_with_valid_token(self, test_client, auth_headers):
        """Test accessing protected endpoint with valid token"""
        response = test_client.get("/api/devices", headers=auth_headers)
        
        assert response.status_code in [200, 403]  # 200 if has permission, 403 if not
