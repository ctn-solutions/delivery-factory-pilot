# Delivery qualification fixture

This public repository contains synthetic code only. It is separate from customer
repositories and has no production deployment, credentials, or customer data.

The baseline is a small Python standard-library package and executable tests.
Pull requests and changes to the default branch run the same test suite.

Required controls for the default branch:

- Passing `synthetic-tests` check on the current change.
- Independent pull-request approval, with stale approvals dismissed.
- Protection applies to administrators; force pushes and deletion are prohibited.

Successful tests do not demonstrate that an external delivery service is live.
This repository is a qualification target, not a production service.

Run the fixture locally with `python3 -m unittest discover -s tests -v`.
