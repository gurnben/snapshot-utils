# Snapshot Sifter

Separating the wheat from the chaff in MCE/ACM snapshots - determining which components are up to date or out of date!

## Install

Developed with Python 3.11!

```
pip3 install -r requirements.txt
```

## Run

```
export GITHUB_TOKEN=<your-github-token>
# Optional: export GITHUB_ORG=<github-org-for-pipeline-repo>
python3 sifter.py <pipeline-repo-name> <pipeline-branch-name> <expected-component-repo-branch>
```
