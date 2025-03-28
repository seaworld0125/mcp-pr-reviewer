#!/usr/bin/env python3
"""
Test script for PR review functionality.
This script directly tests the GitHub PR review functions 
without going through the MCP server.
"""

import os
import sys
from dotenv import load_dotenv
from github_integration import add_pr_comment, submit_pr_review

def test_add_pr_comment():
    """Test adding a comment to a PR."""
    # Set your test values here
    repo_owner = "seaworld0125"
    repo_name = "mcp-pr-reviewer"
    pr_number = 2  # PR to comment on
    
    comment = """
## Test Comment from PR Reviewer

This is a test comment from the PR reviewer tool!

- Working on improving PR review functionality
- Testing direct API calls to GitHub
- Validating error handling and response processing

If you see this comment, the test was successful! 🎉
    """
    
    print(f"Adding comment to PR #{pr_number} on {repo_owner}/{repo_name}...")
    
    result = add_pr_comment(repo_owner, repo_name, pr_number, comment)
    
    if result.get("success"):
        print(f"✅ Comment added successfully!")
        print(f"Comment URL: {result.get('comment_url')}")
    else:
        print(f"❌ Failed to add comment: {result.get('error')}")
    
    return result

def test_submit_pr_review():
    """Test submitting a review to a PR."""
    # Set your test values here
    repo_owner = "seaworld0125"
    repo_name = "mcp-pr-reviewer"
    pr_number = 2  # PR to review
    
    review_body = """
## Test Review from PR Reviewer

This is a test review from the PR reviewer tool!

### What's Working Well
- The implementation looks good
- Error handling is comprehensive
- Types are well defined

### Improvement Suggestions
- Consider adding more unit tests
- Documentation could be enhanced

Overall, great work! This review was submitted automatically by the test script.
    """
    
    print(f"Submitting review to PR #{pr_number} on {repo_owner}/{repo_name}...")
    
    result = submit_pr_review(repo_owner, repo_name, pr_number, review_body)
    
    if result.get("success"):
        print(f"✅ Review submitted successfully!")
        print(f"Review URL: {result.get('review_url')}")
    else:
        print(f"❌ Failed to submit review: {result.get('error')}")
    
    return result

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Verify GitHub token is available
    if not os.getenv("GITHUB_TOKEN"):
        print("ERROR: GITHUB_TOKEN not found in environment variables")
        print("Please set GITHUB_TOKEN in your .env file")
        sys.exit(1)
    
    # Run tests
    test_result = None
    
    if len(sys.argv) > 1 and sys.argv[1] == "--review":
        test_result = test_submit_pr_review()
    else:
        test_result = test_add_pr_comment()
    
    # Exit with success/failure code
    sys.exit(0 if test_result.get("success") else 1)
