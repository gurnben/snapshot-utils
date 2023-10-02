# Snapshot Utils

## Snapshot Sifter

Separating the wheat from the chaff in MCE/ACM snapshots - determining which components are up to date or out of date!

### Install

Should support Python 3.6.4 and up, tested with Python 3.9 and 3.11

```
pip3 install -r requirements.txt
```

### Run

```
export GITHUB_TOKEN=<your-github-token>
# Optional: export GITHUB_ORG=<github-org-for-pipeline-repo>
python3 sifter.py <pipeline-repo-name> <pipeline-branch-name> <expected-component-repo-branch>
```

### Interpret Results

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

## Snapshot Sleuth

Searching for when or whether a change entered an MCE/ACM snapshot!

### Install

Should support Python 3.6.4 and up, tested with Python 3.9 and 3.11

```
pip3 install -r requirements.txt
```

### Run

```
export GITHUB_TOKEN=<your-github-token>
# Optional: export GITHUB_ORG=<github-org-for-pipeline-repo>
python3 sleuth.py <pipeline-repo-name> <pipeline-repo-branch> <component-git-repo-shortname> <component-git-sha>
```

### Interpreting Results

Snapshot Sleuth checks to make sure that all components built off of `<component-repo>` contain `<component-sha>`, 1st searching all manifests that are currently in the pipeline repository, and if it's unable to find a direct match to `<component-sha>`, then it will attempt to walk the git history based off of the latest snapshot and manifest to verify that the latest snapshot contains the target commit in its history.  

The resulting output should either indicate a direct hit:
```
$ python3 sleuth.py pipeline 2.7-integration stolostron/multiclusterhub-operator ca84a3444f14bcd39d8905f1dba2c5c60f6a2f8c
All components built from stolostron/multiclusterhub-operator updated to ca84a3444f14bcd39d8905f1dba2c5c60f6a2f8c as of manifest-2023-01-06-23-31-27-2.7.0.json.
```

An indirect hit:
```
$ python3 sleuth.py pipeline 2.7-integration stolostron/multiclusterhub-operator e2b09335e2074f5360d7e2456ee0d3b38a369aff
We weren't able to determine the first snapshot that contained e2b09335e2074f5360d7e2456ee0d3b38a369aff, but we were able to validate that all components in the latest manifest (manifest-2023-02-10-15-54-02-2.7.1.json) have e2b09335e2074f5360d7e2456ee0d3b38a369aff in its git history, so it contains this change.
We would expect this to occur if the snapshot that first contained e2b09335e2074f5360d7e2456ee0d3b38a369aff for stolostron/multiclusterhub-operator had its manifest garbage collected in our weekly cleanup.
```

Or a miss followed by a list of all components sourced from that repository:
```
$ python3 sleuth.py pipeline 2.7-integration stolostron/multicluster-observability-operator f4f18501bc83f530ebeca434da148980a851435a
Changes not found in any snapshot.
The following entries were found for that repo, but some were older than f4f18501bc83f530ebeca434da148980a851435a:
[{'git-repository': 'stolostron/multicluster-observability-operator',
  'git-sha256': 'bea1ed3ef1e448e1478af0ee1a10175a089aa595',
  'image-digest': 'sha256:737c216eae4282a54c4a6805ed0bfa1a8e0d474d66e3005da6d65b6373ab8241',
  'image-key': 'endpoint_monitoring_operator',
  'image-name': 'endpoint-monitoring-operator',
  'image-remote': 'quay.io/stolostron',
  'image-tag': '2.7.0-bea1ed3ef1e448e1478af0ee1a10175a089aa595',
  'image-version': '2.7'},
 {'git-repository': 'stolostron/multicluster-observability-operator',
  'git-sha256': 'c991897c89779e62111d06ab3b53b961ea23c5e8',
  'image-digest': 'sha256:db6f092f7e285733fb0dc44ecc33b18a3287691046c61b913efaecd4f0126e49',
  'image-key': 'grafana_dashboard_loader',
  'image-name': 'grafana-dashboard-loader',
  'image-remote': 'quay.io/stolostron',
  'image-tag': '2.7.0-c991897c89779e62111d06ab3b53b961ea23c5e8',
  'image-version': '2.7'},
 {'git-repository': 'stolostron/multicluster-observability-operator',
  'git-sha256': 'c3e1e947854f3d711afaeccc814e0951a0158af6',
  'image-digest': 'sha256:4896e6955f3a3020871dcd731a8189ff665c7ccef9ca2b53e1c7d07a5761e6c4',
  'image-key': 'metrics_collector',
  'image-name': 'metrics-collector',
  'image-remote': 'quay.io/stolostron',
  'image-tag': '2.7.0-c3e1e947854f3d711afaeccc814e0951a0158af6',
  'image-version': '2.7'},
 {'git-repository': 'stolostron/multicluster-observability-operator',
  'git-sha256': 'b8a6f8771905a91d535a57e4904fac5c1d86f406',
  'image-digest': 'sha256:3bcdd316e31711f0ad9084832d5ee5ba52bc824fcc9e500691f37effb3966943',
  'image-key': 'multicluster_observability_operator',
  'image-name': 'multicluster-observability-operator',
  'image-remote': 'quay.io/stolostron',
  'image-tag': '2.7.0-b8a6f8771905a91d535a57e4904fac5c1d86f406',
  'image-version': '2.7'},
 {'git-repository': 'stolostron/multicluster-observability-operator',
  'git-sha256': 'b0d789368956c7d4f8186e65b3b701c0561c21b8',
  'image-digest': 'sha256:a1c4c007db174777cd984190dc326825746c78e5374ea1e25d6a8ded45b645c1',
  'image-key': 'observability_e2e_test',
  'image-name': 'observability-e2e-test',
  'image-remote': 'quay.io/stolostron',
  'image-tag': '2.7.0-b0d789368956c7d4f8186e65b3b701c0561c21b8',
  'image-version': '2.7'},
 {'git-repository': 'stolostron/multicluster-observability-operator',
  'git-sha256': 'b0d789368956c7d4f8186e65b3b701c0561c21b8',
  'image-digest': 'sha256:b2601053f5ee0088a3fb15d0108c8cde2832f7271749774eefdd042c1a8d5567',
  'image-key': 'rbac_query_proxy',
  'image-name': 'rbac-query-proxy',
  'image-remote': 'quay.io/stolostron',
  'image-tag': '2.7.0-b0d789368956c7d4f8186e65b3b701c0561c21b8',
  'image-version': '2.7'}]
```
