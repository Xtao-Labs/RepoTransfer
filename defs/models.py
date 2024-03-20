from pydantic import BaseModel


class GithubRepo(BaseModel):
    name: str
    full_name: str
    private: bool
    html_url: str
    clone_url: str
