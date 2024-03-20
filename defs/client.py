from env import URL, TOKEN

from httpx import AsyncClient, TimeoutException


class GiteaError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return f"[{self.status_code}] {self.message}"


def retry(func):
    async def wrapper(*args, **kwargs):
        for _ in range(3):
            try:
                return await func(*args, **kwargs)
            except TimeoutException:
                continue
        raise GiteaError(500, "Failed to get response after 3 retries")

    return wrapper


class Gitea:
    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token
        self.client = AsyncClient(timeout=10)
        self.headers = {
            "Content-type": "application/json",
        }
        if token:
            self.headers["Authorization"] = "token " + token

    def __get_url(self, endpoint):
        url = self.url + "/api/v1" + endpoint
        return url

    @staticmethod
    def parse_result(result) -> dict:
        """Parses the result-JSON to a dict."""
        if result.text and len(result.text) > 3:
            return result.json()
        return {}

    @retry
    async def requests_get(self, endpoint: str, params: dict = None) -> dict:
        combined_params = {}
        if not params:
            params = {}
        combined_params.update(params)
        request = await self.client.get(
            url=self.__get_url(endpoint), headers=self.headers, params=combined_params
        )
        if request.status_code not in [200, 201]:
            message = f"Received status code: {request.status_code} ({request.url})"
            if request.status_code in [403]:
                message = f"Unauthorized: {request.url} - Check your permissions and try again! ({message})"
            raise GiteaError(request.status_code, message)
        return self.parse_result(request)

    @retry
    async def requests_post(self, endpoint: str, data: dict):
        request = await self.client.post(
            url=self.__get_url(endpoint), headers=self.headers, json=data,
        )
        if request.status_code not in [200, 201, 202]:
            raise GiteaError(
                request.status_code,
                f"Received status code: {request.status_code} ({request.url}), {request.text}"
            )
        return self.parse_result(request)

    async def get_version(self) -> str:
        result = await self.requests_get("/version")
        return result["version"]

    async def migrate_repo(self, owner: str, repo_name: str, git_url: str):
        result = await self.requests_post(
            "/repos/migrate",
            data={
                "clone_addr": git_url,
                "repo_name": repo_name,
                "repo_owner": owner,
                "mirror": True,
            },
        )
        return result


gitea = Gitea(URL, TOKEN)
