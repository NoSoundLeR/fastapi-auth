class User:
    def __init__(self, data=None):
        self.data = data
        if data is None:
            self.is_authenticated = False
            self.is_admin = False
            self.id = None
            self.username = None
        else:
            self.is_authenticated = True
            self.is_admin = "admin" in self.data.get("permissions")
            self.id = int(self.data.get("id"))
            self.username = self.data.get("username")

    @classmethod
    async def create(cls, token: str, backend):
        data = await backend.decode_token(token)
        return cls(data)
