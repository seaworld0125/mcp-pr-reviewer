import sys
import os
import traceback
from typing import Any, List, Dict, Optional
from mcp.server.fastmcp import FastMCP
from github_integration import fetch_pr_changes, submit_pr_review, add_pr_comment
from notion_client import Client
from dotenv import load_dotenv

class PRAnalyzer:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize MCP Server
        self.mcp = FastMCP("github_pr_analysis")
        print("MCP Server initialized", file=sys.stderr)
        
        # Initialize Notion client
        self._init_notion()
        
        # Register MCP tools
        self._register_tools()
        
        # Set resource methods handler
        self.mcp.resource_methods_handler = self._handle_resource_methods
    
    def _init_notion(self):
        """Initialize the Notion client with API key and page ID."""
        try:
            self.notion_api_key = os.getenv("NOTION_API_KEY")
            self.notion_page_id = os.getenv("NOTION_PAGE_ID")
            
            if not self.notion_api_key or not self.notion_page_id:
                raise ValueError("Missing Notion API key or page ID in environment variables")
            
            self.notion = Client(auth=self.notion_api_key)
            print(f"Notion client initialized successfully", file=sys.stderr)
            print(f"Using Notion page ID: {self.notion_page_id}", file=sys.stderr)
        except Exception as e:
            print(f"Error initializing Notion client: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)
    
    async def _handle_resource_methods(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP protocol resource methods."""
        print(f"Handling resource method: {method}", file=sys.stderr)
        
        if method == "resources/list":
            print("Processing resources/list request", file=sys.stderr)
            return {
                "resources": [
                    {
                        "name": "github_pr", 
                        "description": "GitHub PR Analysis tools",
                        "tools": [
                            {
                                "name": "fetch_pr",
                                "description": "Fetch changes from a GitHub pull request",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "repo_owner": {"type": "string"},
                                        "repo_name": {"type": "string"},
                                        "pr_number": {"type": "integer"}
                                    },
                                    "required": ["repo_owner", "repo_name", "pr_number"]
                                }
                            },
                            {
                                "name": "create_notion_page",
                                "description": "Create a Notion page with PR analysis",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "content": {"type": "string"}
                                    },
                                    "required": ["title", "content"]
                                }
                            },
                            {
                                "name": "submit_pr_review",
                                "description": "Submit a review to a GitHub pull request",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "repo_owner": {"type": "string"},
                                        "repo_name": {"type": "string"},
                                        "pr_number": {"type": "integer"},
                                        "review_body": {"type": "string"},
                                        "review_state": {
                                            "type": "string", 
                                            "enum": ["COMMENT", "APPROVE", "REQUEST_CHANGES"],
                                            "default": "COMMENT"
                                        },
                                        "comments": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "path": {"type": "string"},
                                                    "position": {"type": "integer"},
                                                    "body": {"type": "string"}
                                                }
                                            }
                                        }
                                    },
                                    "required": ["repo_owner", "repo_name", "pr_number", "review_body"]
                                }
                            },
                            {
                                "name": "add_pr_comment",
                                "description": "Add a comment to a GitHub pull request",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "repo_owner": {"type": "string"},
                                        "repo_name": {"type": "string"},
                                        "pr_number": {"type": "integer"},
                                        "comment": {"type": "string"}
                                    },
                                    "required": ["repo_owner", "repo_name", "pr_number", "comment"]
                                }
                            }
                        ]
                    }
                ]
            }
        else:
            print(f"Unknown resource method: {method}", file=sys.stderr)
            return {}
    
    def _register_tools(self):
        """Register MCP tools for PR analysis."""
        @self.mcp.tool()
        async def fetch_pr(repo_owner: str, repo_name: str, pr_number: int) -> Dict[str, Any]:
            """Fetch changes from a GitHub pull request."""
            print(f"Fetching PR #{pr_number} from {repo_owner}/{repo_name}", file=sys.stderr)
            try:
                pr_info = fetch_pr_changes(repo_owner, repo_name, pr_number)
                if pr_info is None:
                    print("No changes returned from fetch_pr_changes", file=sys.stderr)
                    return {}
                print(f"Successfully fetched PR information", file=sys.stderr)
                return pr_info
            except Exception as e:
                print(f"Error fetching PR: {str(e)}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                return {}
        
        @self.mcp.tool()
        async def create_notion_page(title: str, content: str) -> str:
            """Create a Notion page with PR analysis."""
            print(f"Creating Notion page: {title}", file=sys.stderr)
            try:
                self.notion.pages.create(
                    parent={"type": "page_id", "page_id": self.notion_page_id},
                    properties={"title": {"title": [{"text": {"content": title}}]}},
                    children=[{
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{
                                "type": "text",
                                "text": {"content": content}
                            }]
                        }
                    }]
                )
                print(f"Notion page '{title}' created successfully!", file=sys.stderr)
                return f"Notion page '{title}' created successfully!"
            except Exception as e:
                error_msg = f"Error creating Notion page: {str(e)}"
                print(error_msg, file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                return error_msg
        
        @self.mcp.tool()
        async def submit_pr_review(
            repo_owner: str, 
            repo_name: str, 
            pr_number: int, 
            review_body: str, 
            review_state: str = "COMMENT", 
            comments: Optional[List[Dict[str, Any]]] = None
        ) -> Dict[str, Any]:
            """Submit a review to a GitHub pull request."""
            print(f"Submitting review for PR #{pr_number} from {repo_owner}/{repo_name}", file=sys.stderr)
            try:
                review_response = submit_pr_review(
                    repo_owner, 
                    repo_name, 
                    pr_number, 
                    review_body, 
                    review_state, 
                    comments
                )
                
                if "error" in review_response:
                    print(f"Error in submit_pr_review: {review_response['error']}", file=sys.stderr)
                    return {"success": False, "error": review_response["error"]}
                
                print(f"Successfully submitted PR review", file=sys.stderr)
                return {"success": True, "review_id": review_response.get("id"), "review_url": review_response.get("html_url")}
            except Exception as e:
                error_msg = f"Error submitting PR review: {str(e)}"
                print(error_msg, file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                return {"success": False, "error": str(e)}
        
        @self.mcp.tool()
        async def add_pr_comment(
            repo_owner: str, 
            repo_name: str, 
            pr_number: int, 
            comment: str
        ) -> Dict[str, Any]:
            """Add a comment to a GitHub pull request."""
            print(f"Adding comment to PR #{pr_number} from {repo_owner}/{repo_name}", file=sys.stderr)
            try:
                comment_response = add_pr_comment(
                    repo_owner, 
                    repo_name, 
                    pr_number, 
                    comment
                )
                
                if "error" in comment_response:
                    print(f"Error in add_pr_comment: {comment_response['error']}", file=sys.stderr)
                    return {"success": False, "error": comment_response["error"]}
                
                print(f"Successfully added PR comment", file=sys.stderr)
                return {"success": True, "comment_id": comment_response.get("id"), "comment_url": comment_response.get("html_url")}
            except Exception as e:
                error_msg = f"Error adding PR comment: {str(e)}"
                print(error_msg, file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                return {"success": False, "error": str(e)}
    
    def run(self):
        """Start the MCP server."""
        try:
            print("Running MCP Server for GitHub PR Analysis...", file=sys.stderr)
            self.mcp.run(transport="stdio")
        except Exception as e:
            print(f"Fatal Error in MCP Server: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    analyzer = PRAnalyzer()
    analyzer.run() 