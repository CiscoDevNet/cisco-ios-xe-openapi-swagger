# Vendored third-party libraries

These files are byte-identical copies of upstream npm releases, vendored so the
site's UI libraries run with zero egress (air-gapped / high-security
environments). Note: the public GitHub Pages deployment additionally loads
Microsoft Clarity analytics (`*.clarity.ms`) via `assets/js/sw-register.js`;
remove that block for a fully air-gapped install. SHA-384
hashes below were verified against the same SRI values previously pinned in our
HTML when the assets were served from `cdn.jsdelivr.net`.

| File | Upstream | Version | SHA-384 (base64) | License |
|------|----------|---------|------------------|---------|
| `swagger-ui-5.31.0/swagger-ui.css` | [swagger-ui-dist](https://www.npmjs.com/package/swagger-ui-dist) | 5.31.0 | `KX9Rx9vM1AmUNAn07bPAiZhFD4C8jdNgG6f5MRNvR+EfAxs2PmMFtUUazui7ryZQ` | Apache-2.0 |
| `swagger-ui-5.31.0/swagger-ui-bundle.js` | [swagger-ui-dist](https://www.npmjs.com/package/swagger-ui-dist) | 5.31.0 | `cxafBeQ+zYROeFafGFxtFbnp1ICqeS9mG7+f0WWSHzhnrUvwg9Za5CCw6wgrHA7K` | Apache-2.0 |
| `swagger-ui-5.31.0/swagger-ui-standalone-preset.js` | [swagger-ui-dist](https://www.npmjs.com/package/swagger-ui-dist) | 5.31.0 | `6DNyIQAo3wcTAtOv9yarCKSm1Vhxwkg5ZHgsQ9Y4gD1NuzRgK4+HmCyRbEKkpJ66` | Apache-2.0 |
| `fuse.js` | [fuse.js](https://www.npmjs.com/package/fuse.js) | 7.0.0 | `PCSoOZTpbkikBEtd/+uV3WNdc676i9KUf01KOA8CnJotvlx8rRrETbDuwdjqTYvt` | Apache-2.0 |
| `chart.umd.js` | [chart.js](https://www.npmjs.com/package/chart.js) | 4.4.0 | `FcQlsUOd0TJjROrBxhJdUhXTUgNJQxTMcxZe6nHbaEfFL1zjQ+bq/uRoBQxb0KMo` | MIT |

## Refresh procedure

Use `scripts/refresh_vendor.ps1` (or its `.py` equivalent) to re-download and
re-verify when bumping versions. Update the SRI hashes in this README and in
every consumer (`index.html`, `swagger-*-model/index.html`).
