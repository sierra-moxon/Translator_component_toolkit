import argparse
from .TCT import *

from .translator_node import TranslatorNode

from . import name_resolver, node_normalizer, trapi, translator_kpinfo

# MCP Server functionality
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
