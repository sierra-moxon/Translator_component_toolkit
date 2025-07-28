import argparse
from .server import mcp

def main():
    """MCP Translator: Biomedical Translator Component Toolkit MCP Server."""
    parser = argparse.ArgumentParser(
        description="Provides access to biomedical translator tools including name resolution, node normalization, knowledge provider info, and query orchestration."
    )
    parser.parse_args()
    mcp.run()

if __name__ == "__main__":
    main()