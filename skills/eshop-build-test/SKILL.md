---
name: eshop-build-test
description: Build, test, and run the dotnet/eShop reference app correctly. Use whenever building, testing, or running eShop (backend services, WebApp, ClientApp/MAUI, or the AppHost), or before validating any change in the dotnet/eShop repo.
---

Use this skill whenever a task involves building, testing, or running any part of the `dotnet/eShop` repo, or validating a change before calling it done.

## Repository map

- Aspire entry point: `src/eShop.AppHost/eShop.AppHost.csproj` — orchestrates local end-to-end runs.
- Backend services: `src/Catalog.API`, `src/Basket.API`, `src/Identity.API`, `src/Ordering.API`, plus supporting projects `src/EventBus*`, `src/IntegrationEventLogEF`, `src/Shared`.
- UI projects: `src/WebApp`, `src/WebAppComponents`, `src/HybridApp`, `src/ClientApp` (MAUI).
- Browser e2e tests: `e2e/` (Playwright, see `package.json`).

## Build and test defaults

Trust `global.json` for SDK selection — the checkout may pin a newer .NET SDK than what `README.md` mentions.

For most web and backend changes, mirror `.github/workflows/pr-validation.yml`:

```
dotnet build eShop.Web.slnf
dotnet test --solution eShop.Web.slnf --no-build --no-progress --output detailed
```

For MAUI/`src/ClientApp` changes, treat it as a separate validation slice (CI runs it on Windows with MAUI workloads) and mirror `.github/workflows/pr-validation-maui.yml`:

```
dotnet build src/ClientApp/ClientApp.csproj
dotnet test --project tests/ClientApp.UnitTests/ClientApp.UnitTests.csproj --no-progress --output detailed
```

Run the full application locally with:

```
dotnet run --project src/eShop.AppHost/eShop.AppHost.csproj
```

Functional tests and AppHost-backed runs require Docker.

## Conventions to respect

- `Directory.Build.props` sets `TreatWarningsAsErrors=true` and `UseArtifactsOutput=true` — build output lands under `artifacts/`, and warnings fail the build.
- Prefer project-scoped edits and validation over solution-wide changes; prefer `eShop.Web.slnf` over the full `eShop.slnx` for routine work.
- Preserve the conventions already used by the touched project; do not add new libraries or frameworks unless the task requires them.
- Add or update the nearest unit or functional test for every behavior change.
- For Azure deployment behavior, follow the `azd` flow in `README.md` rather than inventing repo-specific deployment steps.

## Workflow

1. Determine which slice is being touched (web/backend vs. `src/ClientApp`) and pick the matching build/test commands above.
2. Build first, then run tests with `--no-build` against the same solution/project.
3. If the change touches a single backend service (`Catalog.API`, `Basket.API`, `Ordering.API`, `Identity.API`), prefer the `eshop-backend-fixer` agent's scope rules over broad edits.
4. Report which commands were run and their result — do not claim a change is validated without running the matching build/test commands.
