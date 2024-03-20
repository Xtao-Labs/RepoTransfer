from typing import List

from defs.models import GithubRepo

from httpx import AsyncClient


async def get_github_repos(org_name: str) -> List[GithubRepo]:
    async with AsyncClient() as client:
        resp = await client.get(f"https://api.github.com/orgs/{org_name}/repos")
        data = resp.json()
        return [GithubRepo(**repo) for repo in data]
