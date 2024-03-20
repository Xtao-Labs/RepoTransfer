from defs.github import get_github_repos
from defs.client import gitea, GiteaError


async def main():
    print("gitea version:", await gitea.get_version())
    org_name = input("Please input the org name: ")
    repos = await get_github_repos(org_name)
    for repo in repos:
        if repo.private:
            continue
        try:
            await gitea.migrate_repo(org_name, repo.name, repo.clone_url)
            print(f"Repo {repo.name} migrated successfully!")
        except GiteaError as e:
            if e.status_code == 409:
                print(f"Repo {repo.name} already exists!")
            else:
                print(f"Failed to migrate repo {repo.name}: {e}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
