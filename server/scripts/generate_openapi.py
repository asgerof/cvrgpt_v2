#!/usr/bin/env python3
"""
Script to generate OpenAPI spec without running the full server.
This avoids import issues with MCP and other dependencies.
"""

import json
from typing import Dict, Any


def create_openapi_spec() -> Dict[str, Any]:
    """Create a basic OpenAPI spec for the API endpoints."""
    return {
        "openapi": "3.1.0",
        "info": {"title": "CVRGPT Server", "version": "0.1.0"},
        "paths": {
            "/healthz": {
                "get": {
                    "summary": "Health Check",
                    "operationId": "health_check",
                    "responses": {
                        "200": {
                            "description": "Successful Response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "provider": {"type": "string"},
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/readyz": {
                "get": {
                    "summary": "Readiness Check",
                    "operationId": "readiness_check",
                    "responses": {
                        "200": {
                            "description": "Service Ready",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"status": {"type": "string"}},
                                    }
                                }
                            },
                        },
                        "503": {
                            "description": "Service Not Ready",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"detail": {"type": "string"}},
                                    }
                                }
                            },
                        },
                    },
                }
            },
            "/v1/search": {
                "get": {
                    "summary": "Search Companies",
                    "operationId": "search_companies",
                    "security": [{"ApiKeyAuth": []}],
                    "parameters": [
                        {
                            "name": "q",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Search query",
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer", "default": 10},
                            "description": "Maximum number of results",
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Search Results",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "items": {
                                                "type": "array",
                                                "items": {"$ref": "#/components/schemas/Company"},
                                            },
                                            "citations": {
                                                "type": "array",
                                                "items": {"$ref": "#/components/schemas/Citation"},
                                            },
                                        },
                                    }
                                }
                            },
                        },
                        "401": {"$ref": "#/components/responses/UnauthorizedError"},
                        "429": {"$ref": "#/components/responses/RateLimitError"},
                    },
                }
            },
            "/v1/company/{cvr}": {
                "get": {
                    "summary": "Get Company Details",
                    "operationId": "get_company",
                    "security": [{"ApiKeyAuth": []}],
                    "parameters": [
                        {
                            "name": "cvr",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "CVR number",
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Company Details",
                            "headers": {
                                "ETag": {"schema": {"type": "string"}},
                                "Cache-Control": {"schema": {"type": "string"}},
                            },
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Company"}
                                }
                            },
                        },
                        "304": {"description": "Not Modified"},
                        "401": {"$ref": "#/components/responses/UnauthorizedError"},
                        "404": {"$ref": "#/components/responses/NotFoundError"},
                        "429": {"$ref": "#/components/responses/RateLimitError"},
                    },
                }
            },
            "/v1/filings/{cvr}": {
                "get": {
                    "summary": "List Company Filings",
                    "operationId": "list_filings",
                    "security": [{"ApiKeyAuth": []}],
                    "parameters": [
                        {
                            "name": "cvr",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "CVR number",
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer", "default": 10},
                            "description": "Maximum number of results",
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Company Filings",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "filings": {
                                                "type": "array",
                                                "items": {"$ref": "#/components/schemas/Filing"},
                                            },
                                            "citations": {
                                                "type": "array",
                                                "items": {"$ref": "#/components/schemas/Citation"},
                                            },
                                        },
                                    }
                                }
                            },
                        },
                        "401": {"$ref": "#/components/responses/UnauthorizedError"},
                        "429": {"$ref": "#/components/responses/RateLimitError"},
                    },
                }
            },
            "/v1/accounts/latest/{cvr}": {
                "get": {
                    "summary": "Get Latest Accounts",
                    "operationId": "get_latest_accounts",
                    "security": [{"ApiKeyAuth": []}],
                    "parameters": [
                        {
                            "name": "cvr",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "CVR number",
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Latest Accounts",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/AccountsResponse"}
                                }
                            },
                        },
                        "401": {"$ref": "#/components/responses/UnauthorizedError"},
                        "404": {"$ref": "#/components/responses/NotFoundError"},
                        "429": {"$ref": "#/components/responses/RateLimitError"},
                    },
                }
            },
            "/v1/compare/{cvr}": {
                "get": {
                    "summary": "Compare Company Accounts",
                    "operationId": "compare_accounts",
                    "security": [{"ApiKeyAuth": []}],
                    "parameters": [
                        {
                            "name": "cvr",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "CVR number",
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Account Comparison",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/CompareResponse"}
                                }
                            },
                        },
                        "401": {"$ref": "#/components/responses/UnauthorizedError"},
                        "404": {"$ref": "#/components/responses/NotFoundError"},
                        "429": {"$ref": "#/components/responses/RateLimitError"},
                    },
                }
            },
        },
        "components": {
            "securitySchemes": {
                "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "x-api-key"}
            },
            "schemas": {
                "Company": {
                    "type": "object",
                    "properties": {
                        "cvr": {"type": "string"},
                        "name": {"type": "string"},
                        "address": {"type": "string"},
                        "status": {"type": "string"},
                    },
                },
                "Filing": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "type": {"type": "string"},
                        "date": {"type": "string"},
                        "url": {"type": "string"},
                    },
                },
                "Citation": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string"},
                        "url": {"type": "string"},
                        "path": {"type": "string"},
                        "note": {"type": "string"},
                    },
                },
                "AccountsResponse": {
                    "type": "object",
                    "properties": {
                        "accounts": {"type": "object"},
                        "citations": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Citation"},
                        },
                    },
                },
                "CompareResponse": {
                    "type": "object",
                    "properties": {
                        "current_period": {"type": "string"},
                        "previous_period": {"type": "string"},
                        "key_changes": {"type": "array", "items": {"type": "object"}},
                        "narrative": {"type": "string"},
                        "sources": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Citation"},
                        },
                    },
                },
            },
            "responses": {
                "UnauthorizedError": {
                    "description": "Authentication required",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "detail": {
                                        "type": "object",
                                        "properties": {
                                            "code": {"type": "string"},
                                            "message": {"type": "string"},
                                        },
                                    }
                                },
                            }
                        }
                    },
                },
                "NotFoundError": {
                    "description": "Resource not found",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"detail": {"type": "string"}},
                            }
                        }
                    },
                },
                "RateLimitError": {
                    "description": "Rate limit exceeded",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"detail": {"type": "string"}},
                            }
                        }
                    },
                },
            },
        },
    }


if __name__ == "__main__":
    spec = create_openapi_spec()
    with open("openapi.json", "w") as f:
        json.dump(spec, f, indent=2)
    print("✅ Generated openapi.json")
