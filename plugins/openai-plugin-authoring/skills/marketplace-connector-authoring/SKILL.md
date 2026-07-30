---
name: marketplace-connector-authoring
description: Add or revise an OpenAI plugin connector that exposes authenticated external-service tools. Use when a ChatGPT or Codex plugin needs a user-connected service rather than a standalone skill or MCP server.
---

This is an OpenAI-specific component. Do not add a connector shim to the Claude Code or GitHub Copilot packages.

## Decide and design

1. Use a connector when the plugin needs an authenticated integration with an external service. Use an MCP server instead when server-backed tools or shared context are the better boundary.
2. Define every exposed operation, input and output schema, errors, data sharing, authorization scope, and user-visible consent path before implementation.
3. Keep connector resources and optional UI within the OpenAI native package. Never reference a Claude or GitHub sibling package.
4. Use host-managed authentication and secret configuration. Do not embed credentials in skills, manifests, scripts, or examples.

## Validate

Install the OpenAI package through its marketplace flow, complete the real connection or authentication path, and exercise every exposed operation. Verify both success and authorization-failure behavior before claiming the connector works.