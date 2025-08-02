{
  "openapi": "3.1.0",
  "info": { "title": "Noah Memory API", "version": "1.0.1" },
  "servers": [{ "url": "https://noah-engine.onrender.com" }],
  "paths": {
    "/memory/add": {
      "post": {
        "operationId": "addMemory",
        "summary": "Add or update a memory key/value",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": { "$ref": "#/components/schemas/AddMemoryRequest" },
              "example": { "key": "voice", "value": "deep male Hebrew" }
            }
          }
        },
        "responses": {
          "200": { "description": "Added/updated", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/StatusResponse" } } } },
          "400": { "description": "Bad request", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/ErrorResponse" } } } },
          "403": { "description": "Forbidden", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/ErrorResponse" } } } }
        },
        "security": [{ "ApiKeyAuth": [] }]
      }
    },
    "/memory/list": {
      "get": {
        "operationId": "listMemory",
        "summary": "List all memory items",
        "responses": {
          "200": { "description": "List", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/MemoryListResponse" } } } },
          "403": { "description": "Forbidden", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/ErrorResponse" } } } }
        },
        "security": [{ "ApiKeyAuth": [] }]
      }
    },
    "/memory/get": {
      "get": {
        "operationId": "getMemory",
        "summary": "Get item by key",
        "parameters": [
          { "name": "key", "in": "query", "required": true, "schema": { "type": "string" } }
        ],
        "responses": {
          "200": { "description": "Item or null", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/GetMemoryResponse" } } } },
          "400": { "description": "Missing key", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/ErrorResponse" } } } },
          "403": { "description": "Forbidden", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/ErrorResponse" } } } }
        },
        "security": [{ "ApiKeyAuth": [] }]
      }
    },
    "/memory/delete": {
      "delete": {
        "operationId": "deleteMemory",
        "summary": "Delete an item by key",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": { "$ref": "#/components/schemas/DeleteMemoryRequest" },
              "example": { "key": "voice" }
            }
          }
        },
        "responses": {
          "200": { "description": "Deleted", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/StatusResponse" } } } },
          "400": { "description": "Missing key", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/ErrorResponse" } } } },
          "403": { "description": "Forbidden", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/ErrorResponse" } } } }
        },
        "security": [{ "ApiKeyAuth": [] }]
      }
    }
  },
  "components": {
    "securitySchemes": {
      "ApiKeyAuth": { "type": "apiKey", "in": "header", "name": "X-API-Key" }
    },
    "schemas": {
      "MemoryItem": {
        "type": "object",
        "properties": { "key": { "type": "string" }, "value": { "type": "string" } },
        "required": ["key", "value"],
        "additionalProperties": false
      },
      "AddMemoryRequest": {
        "type": "object",
        "properties": { "key": { "type": "string" }, "value": { "type": "string" } },
        "required": ["key", "value"],
        "additionalProperties": false
      },
      "DeleteMemoryRequest": {
        "type": "object",
        "properties": { "key": { "type": "string" } },
        "required": ["key"],
        "additionalProperties": false
      },
      "StatusResponse": {
        "type": "object",
        "properties": { "status": { "type": "string", "enum": ["ok", "error"] } },
        "required": ["status"],
        "additionalProperties": false
      },
      "ErrorResponse": {
        "type": "object",
        "properties": { "status": { "type": "string", "enum": ["error"] }, "error": { "type": "string" } },
        "required": ["status", "error"],
        "additionalProperties": false
      },
      "MemoryListResponse": {
        "type": "object",
        "properties": {
          "status": { "type": "string", "enum": ["ok", "error"] },
          "data": { "type": "array", "items": { "$ref": "#/components/schemas/MemoryItem" } }
        },
        "required": ["status", "data"],
        "additionalProperties": false
      },
      "GetMemoryResponse": {
        "type": "object",
        "properties": {
          "status": { "type": "string", "enum": ["ok", "error"] },
          "item": { "oneOf": [ { "$ref": "#/components/schemas/MemoryItem" }, { "type": "null" } ] }
        },
        "required": ["status", "item"],
        "additionalProperties": false
      }
    }
  }
}
