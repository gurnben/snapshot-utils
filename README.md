# Snapshot Sifter

Separating the wheat from the chaff in MCE/ACM snapshots - determining which components are up to date or out of date!

## Install

Should support Python 3.6.4 and up, tested with Python 3.9 and 3.11

```
pip3 install -r requirements.txt
```

## Run

```
export GITHUB_TOKEN=<your-github-token>
# Optional: export GITHUB_ORG=<github-org-for-pipeline-repo>
python3 sifter.py <pipeline-repo-name> <pipeline-branch-name> <expected-component-repo-branch>
```

## Interpret Results

Snapshot Sifter will log when it detects issues with components in a manifest.  For example:
```
[COMPONENT_NAME] isn't up to date. # Repo and branch found, but commit out of date
[COMPONENT_NAME] has no branch release-2.8 # Repo found, but no expected-component-repo-branch
[COMPONENT_NAME] git-repository invalid # Repo not found / invalid
```

Snapshot Sifter will also create a file, named after the latest snapshot manifest, which includes the following data in JSON format:
```
    "COMPONENT_NAME": {
        "branch": "LINK_TO_BRANCH_IF_FOUND",
        "commit": "LINK_TO_COMMIT_IF_FOUND",
        "found_branch": true,
        "found_repo": true,
        "repo": "LINK_TO_REPO_IF_FOUND",
        "up_to_date": true
    },
```
