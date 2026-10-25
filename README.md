# Delivery qualification fixture

This public repository contains synthetic code only. It is separate from customer
repositories and has no customer production deployment, credentials, or customer data.

The baseline is a small Python standard-library package and executable tests.
Pull requests and changes to the default branch run the same test suite.

Required controls for the default branch:

- Passing `synthetic-tests` check on the current change.
- Independent pull-request approval, with stale approvals dismissed.
- Protection applies to administrators; force pushes and deletion are prohibited.

Successful tests do not demonstrate that an external delivery service is live.
This repository is a qualification target, not a production service.

Run the fixture locally with `python3 -m unittest discover -s tests -v`.

## Synthetic deployment target

The intended target is GitHub Pages for `ctn-solutions/delivery-factory-pilot`,
served at `https://ctn-solutions.github.io/delivery-factory-pilot/` when Pages is
configured to use GitHub Actions. Adding this source does not enable Pages or
prove that any external delivery service deployed it.

The Pages workflow runs only for a push to `main` or a manual dispatch on `main`.
It checks out the exact triggering revision. Its fixed Python validator packages
only `docs/site/index.html`, a committed, non-executable regular file of at most
64 KiB. It refuses links, extra files, dirty content and pre-existing output.
It executes no site-provided build commands, package installers or plugins.
Build has read access to source; only the deployment job receives Pages write
and OIDC token permissions, under the `github-pages` environment. Existing
branch protections and the required `synthetic-tests` check remain applicable.

Each artifact contains `deployment-receipt.json` with the exact repository,
source commit and SHA-256 of the published HTML bytes. Live verification must
fetch both the receipt and HTML from the configured Pages URL, compare the
receipt commit to the merged revision, and verify the HTML digest. A successful
workflow alone is insufficient. Receipts contain no secrets or customer data;
the public URL may be replaced by a later deployment, so retain the matching
workflow artifact and deployment record as historical evidence.

Initial setup requires configuring the repository's Pages source as GitHub
Actions and restricting the `github-pages` environment to `main`. This setup
must be completed and independently verified before claiming automatic minor
changes reach this target. No Pages setup or deployment has been performed by
adding these files.
