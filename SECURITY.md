# Security Policy

## Supported release

Security fixes are targeted at the latest LyricVid release on `main`.

## Credential policy

LyricVid's YouTube integration uses a local OAuth Desktop client and cached user token. These files are **runtime credentials, not repository assets**. Never commit or attach them to a GitHub issue, release, Docker image, CI artifact, or documentation screenshot.

Blocked/ignored credential paths include:

```text
.secrets/
client_secret_*.json
youtube-oauth.json
youtube-token.json
credentials.json
```

Before every push, run:

```bash
./scripts/validate-no-secrets.sh
```

CI runs the same check.

## If a credential is exposed

1. Revoke or rotate the affected OAuth client/token as appropriate.
2. Remove the secret from the working tree.
3. Remove it from Git history if it was committed; a later deletion commit does not erase history.
4. Force-push rewritten history only after coordinating with collaborators.
5. Re-authenticate LyricVid and generate a fresh local token.

## CI security checks

The repository currently validates:

- forbidden tracked credential paths and high-confidence secret patterns;
- Python runtime dependencies with `pip-audit`;
- Python source with `bandit`;
- Remotion/npm runtime dependencies with `npm audit`;
- shell syntax;
- D2 architecture compilation;
- package version consistency;
- Python compatibility and tests;
- wheel/sdist metadata with `twine check`;
- Docker image buildability.

Container releases are published to GHCR with GitHub artifact provenance attestations. OAuth credentials are not required by CI/CD.

## Reporting a vulnerability

Do not post credentials or exploitable private details in a public issue. Use GitHub's private vulnerability reporting/security-advisory mechanism when available for the repository. Otherwise contact the repository owner privately and include only the minimum reproduction details needed to understand the problem.

## Repository-specific Secret Guard

In addition to GitHub secret scanning and push protection, LyricVid ships a local/CI scanner tailored to the credentials this project is most likely to handle:

```bash
python scripts/secret-guard.py --self-test
python scripts/secret-guard.py
```

It rejects tracked `.secrets/` directories, YouTube OAuth/token JSON files, Google OAuth client/refresh/access secrets, private keys, Google API keys, AWS keys, GitHub tokens, Stripe/OpenAI-style secret keys, service-account key material, and database URLs containing embedded passwords. Google OAuth client IDs by themselves are identifiers rather than secrets and do not fail the scan unless secret-bearing fields are present in the same credential-like document.

A positive finding should be treated as a potential exposure: revoke or rotate the credential first, then remove it from the repository and Git history. Deleting it only in a later commit is not sufficient.
