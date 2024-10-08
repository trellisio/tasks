import pytest

from app.infra.keycloak.auth import KeycloakAuth


class TestKeycloakAuth:
    auth: KeycloakAuth

    @pytest.fixture(autouse=True)
    async def set_up(self):
        self.auth = KeycloakAuth()

    async def test_can_login_user(self):
        res = await self.auth.login("rwhughes91@gmail.com", "password")
        assert res.get("access_token") is not None
        assert res.get("refresh_token") is not None

    async def test_exception_raised_on_bad_login(self):
        with pytest.raises(Exception):
            await self.auth.login("rwhughes91@gmail.com", "wrong-password")

    async def test_can_refresh_token(self):
        res = await self.auth.login("rwhughes91@gmail.com", "password")
        refresh_token = res["refresh_token"]

        res = await self.auth.refresh_token(refresh_token)
        assert res.get("access_token") is not None
        assert res.get("refresh_token") is not None

    async def test_exception_raised_on_bad_refresh_token(self):
        with pytest.raises(Exception):
            await self.auth.refresh_token("token")

    async def test_can_validate_and_decode_jwt(self):
        res = await self.auth.login("rwhughes91@gmail.com", "password")
        token = res["access_token"]
        payload = await self.auth.validate(token)
        assert payload["email"] == "rwhughes91@gmail.com"
        assert payload["roles"] is not None

    async def test_exception_raised_on_validation_of_bad_token(self):
        with pytest.raises(Exception):
            await self.auth.validate("token")

    async def test_returns_false_if_not_role_in_jwt(self):
        res = await self.auth.login("rwhughes91@gmail.com", "password")
        token = res["access_token"]
        has_role = await self.auth.has_role(token, "some-role")
        assert has_role is False

    # async def test_returns_true_if_role_in_jwt(self):
    #     pass
