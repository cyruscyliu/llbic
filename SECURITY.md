# Security Policy

## Supported versions

`llbic` is maintained as a rolling project rather than a set of long-lived release branches.

Security fixes are most likely to land in:

- the default branch on GitHub
- the latest published container images

If you are running an older checkout or image tag, reproduce the issue against the latest version before reporting it.

## Reporting a vulnerability

Please do not open a public issue for a suspected security vulnerability.

Use one of these paths instead:

1. GitHub Security Advisories private reporting for this repository, if available.
2. If private reporting is not available, open a regular issue only after removing exploit details and clearly state that you need a private contact path.

Please include:

- affected `llbic` version, commit, or container tag
- exact command used
- kernel version involved
- impact and expected risk
- reproduction steps or proof of concept
- any relevant logs with secrets removed

You can expect an initial maintainer response on a best-effort basis. After triage, fixes will usually be shipped through the default branch and refreshed container images.

## Scope

Relevant reports include issues such as:

- command injection or unsafe shell handling
- insecure container defaults
- supply-chain or dependency integrity problems in the build flow
- accidental credential or secret exposure in logs or outputs

Issues limited to unsupported upstream kernels, local misconfiguration, or general build failures should go through the normal issue tracker instead.
