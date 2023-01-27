import os, sys, json
from github import Github, UnknownObjectException, GithubException

if __name__ == '__main__':

    if len(sys.argv) < 4:
        print("Usage: python sifter.py <pipeline-repo-name> <pipeline-repo-branch> <component-branch>")
        exit(1)

    org_name = os.getenv('GITHUB_ORG') if os.getenv('GITHUB_ORG') != None else 'stolostron'
    repo = sys.argv[1]
    pipeline_branch = sys.argv[2]
    component_branch = sys.argv[3]

    results = {}
    gh = Github(os.getenv('GITHUB_TOKEN'))
    org = gh.get_organization(org_name)
    pipeline = org.get_repo(repo)
    snapshots = pipeline.get_contents('snapshots', ref=pipeline_branch)
    snapshots.sort(key=lambda s: s.name, reverse=True)
    if len(snapshots) < 1:
        print(f"We found no snapshots in {org}/{repo} branch {pipeline_branch}.")
        exit(0)
    snapshot_name = snapshots[0].name
    manifest = json.loads(snapshots[0].decoded_content)
    for repo in manifest:
        c_org_name, c_repo_name = repo['git-repository'].split('/')
        image_name = repo['image-name']
        results[image_name] = {
            'found_repo': False,
            'found_branch': False,
            'up_to_date': False,
            'repo': "",
            'branch': "",
            'commit': "",
        }
        # Try to find the component in git, report and pass if not found
        try:
            c_org = gh.get_organization(c_org_name)
            c_repo = c_org.get_repo(c_repo_name)
            results[image_name]['found_repo'] = True
            results[image_name]['repo'] = c_repo.html_url
        except UnknownObjectException as ex:
            print(f"[{image_name}] git-repository invalid")
            continue
        # Try to find the new release branch, report and pass if not found
        try:
            c_commit = c_repo.get_branch(component_branch).commit
            results[image_name]['found_branch'] = True
            results[image_name]['branch'] = f"{c_repo.html_url}/tree/{component_branch}"
        except GithubException as ex:
            print(f"[{image_name}] has no branch {component_branch}")
            continue
        if c_commit.sha == repo['git-sha256']:
           results[image_name]['up_to_date'] = True
           results[image_name]['commit'] = c_commit.url
        else:
            print(f"[{image_name}] isn't up to date.")
    with open(f"{snapshot_name}.analysis.json", 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=4, sort_keys=True)
            

