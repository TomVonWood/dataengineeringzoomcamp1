
from prefect.deployments import Deployment
from prefect.filesystems import GitHub
from web_to_gcs_git import etl_web_to_gcs

git_block = GitHub.load("git")

git_dep = Deployment.build_from_flow(
    flow=etl_web_to_gcs,
    name='git-flow'
)

if __name__ == "__main__":
    git_dep.apply()
