import os
import requests
import traceback
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

def fetch_pr_changes(repo_owner: str, repo_name: str, pr_number: int) -> Dict[str, Any]:
    """Fetch changes from a GitHub pull request.
    
    Args:
        repo_owner: The owner of the GitHub repository
        repo_name: The name of the GitHub repository
        pr_number: The number of the pull request to analyze
        
    Returns:
        A dictionary containing PR information and changes
    """
    print(f" Fetching PR changes for {repo_owner}/{repo_name}#{pr_number}")
    
    # Fetch PR details
    pr_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}"
    files_url = f"{pr_url}/files"
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    
    try:
        # Get PR metadata
        pr_response = requests.get(pr_url, headers=headers)
        pr_response.raise_for_status()
        pr_data = pr_response.json()
        
        # Get file changes
        files_response = requests.get(files_url, headers=headers)
        files_response.raise_for_status()
        files_data = files_response.json()
        
        # Combine PR metadata with file changes
        changes = []
        for file in files_data:
            change = {
                'filename': file['filename'],
                'status': file['status'],  # added, modified, removed
                'additions': file['additions'],
                'deletions': file['deletions'],
                'changes': file['changes'],
                'patch': file.get('patch', ''),  # The actual diff
                'raw_url': file.get('raw_url', ''),
                'contents_url': file.get('contents_url', '')
            }
            changes.append(change)
        
        # Add PR metadata
        pr_info = {
            'title': pr_data['title'],
            'description': pr_data['body'],
            'author': pr_data['user']['login'],
            'created_at': pr_data['created_at'],
            'updated_at': pr_data['updated_at'],
            'state': pr_data['state'],
            'total_changes': len(changes),
            'changes': changes
        }
        
        print(f"Successfully fetched {len(changes)} changes")
        return pr_info
        
    except Exception as e:
        print(f"Error fetching PR changes: {str(e)}")
        traceback.print_exc()
        return None

def submit_pr_review(repo_owner: str, repo_name: str, pr_number: int, review_body: str, 
                    review_state: str = "COMMENT", comments: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Submit a review to a GitHub pull request.
    
    Args:
        repo_owner: The owner of the GitHub repository
        repo_name: The name of the GitHub repository
        pr_number: The number of the pull request to review
        review_body: The main review comment body
        review_state: The state of the review ('COMMENT', 'APPROVE', or 'REQUEST_CHANGES')
        comments: Optional list of review comments on specific lines/files
        
    Returns:
        The API response containing the submitted review information
    """
    print(f"Submitting review for {repo_owner}/{repo_name}#{pr_number}")
    
    review_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/reviews"
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Prepare review payload
    review_data = {
        "body": review_body,
        "event": review_state
    }
    
    # Add line-specific comments if provided
    if comments:
        review_data["comments"] = comments
    
    try:
        # Submit the review
        review_response = requests.post(review_url, headers=headers, json=review_data)
        review_response.raise_for_status()
        response_data = review_response.json()
        
        print(f"Successfully submitted review (ID: {response_data.get('id')})")
        return response_data
        
    except Exception as e:
        print(f"Error submitting PR review: {str(e)}")
        traceback.print_exc()
        return {"error": str(e)}

def add_pr_comment(repo_owner: str, repo_name: str, pr_number: int, comment: str) -> Dict[str, Any]:
    """Add a comment to a GitHub pull request.
    
    Args:
        repo_owner: The owner of the GitHub repository
        repo_name: The name of the GitHub repository
        pr_number: The number of the pull request to comment on
        comment: The comment text
        
    Returns:
        The API response containing the comment information
    """
    print(f"Adding comment to {repo_owner}/{repo_name}#{pr_number}")
    
    comment_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{pr_number}/comments"
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    comment_data = {
        "body": comment
    }
    
    try:
        # Submit the comment
        comment_response = requests.post(comment_url, headers=headers, json=comment_data)
        comment_response.raise_for_status()
        response_data = comment_response.json()
        
        print(f"Successfully added comment (ID: {response_data.get('id')})")
        return response_data
        
    except Exception as e:
        print(f"Error adding PR comment: {str(e)}")
        traceback.print_exc()
        return {"error": str(e)}
