import pytest
from app import app, get_github_branches, propagate_fix
from unittest.mock import patch

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

@patch('app.get_github_branches')
@patch('app.propagate_fix')
def test_propagate_bug_fix_with_conflict(mock_propagate_fix, mock_get_github_branches, client):
    mock_get_github_branches.return_value = ['main', 'feature-branch']
    mock_propagate_fix.return_value = [
        "Error cherry-picking commit: Cmd('git') failed due to: exit code(1)\n  cmdline: git cherry-pick 4d6362568587518849869afa158ac9c39b255a9f\n  stdout: 'Auto-merging .gitignore\nCONFLICT (add/add): Merge conflict in .gitignore\nAuto-merging README.md\nCONFLICT (add/add): Merge conflict in README.md'\n  stderr: 'error: could not apply 4d63625... Initial commit\nhint: After resolving the conflicts, mark them with\nhint: \"git add/rm <pathspec>\", then run\nhint: \"git cherry-pick --continue\".\nhint: You can instead skip this commit with \"git cherry-pick --skip\".\nhint: To abort and get back to the state before \"git cherry-pick\", hint: run \"git cherry-pick --abort\"."
    ]

    response = client.post('/propagate-bug-fix', json={
        'branch': 'feature-branch',
        'commit': '4d6362568587518849869afa158ac9c39b255a9f'
    })

    print('Response JSON:', response.json)  # Debug line
    print('Response Status Code:', response.status_code)  # Debug line

    assert response.status_code == 400
    assert 'conflicts' in response.json


@patch('app.get_github_branches')
def test_propagate_bug_fix_invalid_branch(mock_get_github_branches, client):
    mock_get_github_branches.return_value = ['main']
    
    response = client.post('/propagate-bug-fix', json={
        'branch': 'non-existent-branch',
        'commit': 'dummy_commit_hash'
    })

    assert response.status_code == 400
    assert response.json == {"success": False, "error": "Invalid branch specified"}
