import os, sys, json, re, pprint
from github import Github, UnknownObjectException, GithubException

if __name__ == '__main__':

    if len(sys.argv) < 4:
        print("Usage: python sleuth.py <pipeline-repo-name> <pipeline-repo-branch> <component-repo> <component-sha>")
        exit(1)

    org_name = os.getenv('GITHUB_ORG') if os.getenv('GITHUB_ORG') != None else 'stolostron'
    repo = sys.argv[1]
    pipeline_branch = sys.argv[2]
    component_repo = sys.argv[3]
    component_sha = sys.argv[4]

    results = {}
    gh = Github(os.getenv('GITHUB_TOKEN'))
    org = gh.get_organization(org_name)
    pipeline = org.get_repo(repo)
    snapshots = pipeline.get_contents('snapshots', ref=pipeline_branch)

    # Filter out downstream snapshots and gitkeep and sort
    r = re.compile('manifest-([0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2})-[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{1,2}\.json')
    snapshots = list(filter(lambda s: r.search(s.name), snapshots))
    snapshots.sort(key=lambda s: s.name, reverse=False)

    if len(snapshots) < 1:
        print(f"We found no snapshots in {org}/{repo} branch {pipeline_branch}.")
        exit(0)
    match = []
    mismatch = []
    for snapshot in snapshots:
        manifest = json.loads(snapshot.decoded_content)
        c = [component for component in manifest if component['git-repository'] == component_repo]
        match = []
        mismatch = []
        for component in c:
            match.append(component) if component['git-sha256'] == component_sha else mismatch.append(component)
        if len(match) > 0 and len(mismatch) == 0:
            print(f"All components built from {component_repo} updated to {component_sha} as of {snapshot.name}.")
            exit(0)
    
    # If we found no matches, check git history on the components to see if we garbage collectd the target commit.
    if len(match) > 0 and len(mismatch) > 0:
        # We found a partial match, which likely means something went wrong during a publish
        #   from 1 of the component images.
        print(f"Changes not found across all components built from {component_repo}.")
        print(f"The following entries did contain {component_sha}")
        pprint.pprint(match)
        print(f"The following entries did NOT contain {component_sha}:")
        pprint.pprint(mismatch)
    elif len(mismatch) > 0:
        # If we found no matches at all, we should check to see
        #   If we already garbage collected that snapshot
        #   By searching the git history of the target components
        # At this point mismatch will contain the latest snapshot details

        c_org_name, c_repo_name = component_repo.split('/')
        c_org = gh.get_organization(c_org_name)
        c_repo = c_org.get_repo(c_repo_name)

        # Generate a list of unique get shas and then sort them by date
        shas = list(set([c['git-sha256'] for c in mismatch]))
        shas.sort(key = lambda s: c_repo.get_commit(s).commit.author.date, reverse=False)

        # grab the oldest commit sha and the commit date for comparison
        oldest_manifest_sha = shas[0]
        oldest_manifest_date = c_repo.get_commit(oldest_manifest_sha).commit.author.date

        # grab the target commit date for comparison
        target_date = c_repo.get_commit(component_sha).commit.author.date

        # If the oldest commit in a manifest is older than our target, we can assume the target isn't included
        if oldest_manifest_date < target_date:
            print(f"Changes not found in any snapshot.")
            print(f"The following entries were found for that repo, but some were older than {component_sha}:")
            pprint.pprint(mismatch)
            exit(1)

        # If the oldest commit in a manifest is newer than our target, we should validate all manifest
        #    shas and validate that they contain our target.
        for s in shas:
            for c in c_repo.get_commits(s):
                if c.sha == component_sha:
                    # If we found the target sha, we can stop searching this commit's history
                    break
                if c.commit.author.date < target_date:
                    # If we found a commit that is older than our target 
                    #   before we find our target, we can declare failure
                    print(f"Changes not found in any snapshot.")
                    print(f"The following entries were found for that repo, but not all contain {component_sha} in their git history:")
                    pprint.pprint(mismatch)
                    exit(1)

        # If we've made it to this point, we have found that the target commit (component_sha)
        #    is in the git history of every component in the manifest belt off of component_repo
        print(f"We weren't able to determine the first snapshot that contained {component_sha}, but we were able to validate that all components in the latest manifest ({snapshots[len(snapshots) - 1].name}) have {component_sha} in its git history, so it contains this change.")
        print(f"We would expect this to occur if the snapshot that first contained {component_sha} for {component_repo} had its manifest garbage collected in our weekly cleanup.")

    else:
        print("An error occurred, we should've found your snapshot by now!")
        exit(1)
