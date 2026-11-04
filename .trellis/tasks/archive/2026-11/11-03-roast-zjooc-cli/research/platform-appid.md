# Research: Public ZJOOC appid

- Query: Does the current public ZJOOC web client hardcode appid `D1R0m75G`, load it from runtime or server configuration, or derive it from user, course, or session state? Trace its use in request headers and `clientsign`.
- Scope: external
- Date: 2026-11-04

## Findings

The current public web client hardcodes `D1R0m75G` as the default `appid` in its request wrapper. The authenticated student course list loaded from `https://www.zjooc.cn/ucenter/student/course/build/list`. Its first-party JavaScript bundle was fetched on 2026-11-04 with `credentials: "omit"` and returned HTTP 200.

Current bundle: [app.e0f0662a557f6a3463dd1793672249346.js](https://www.zjooc.cn/dist/assets_e0f0662a557f6a3463dd/js/app.e0f0662a557f6a3463dd1793672249346.js?). The filename is the deployed asset name. The source uses UTF-16 code-unit offsets.

At UTF-16 offset 3,681,041, the bundle declares `var Kt="D1R0m75G";`. This default assignment is a literal, not a user, course, or session lookup. The GET method starts at offset 3,685,138. Its optional header argument is `arguments[5]`, used when `arguments.length>5&&void 0!==arguments[5]`. The separate source expressions below occur in this method near offset 3,685,468 and later in the same request path:

- Appid and signature input: `appid:Kt,timestamp:d,nonce:f,clientsign:Vt.a.md5("appid=".concat(Kt,"&timestamp=").concat(d,"&nonce=").concat(f))`
- Caller header merge: `a&&(g=Object.assign(g,a))`
- AJAX endpoint: `url:"/ajax"+l`
- Headers passed to AJAX: `headers:g`

These are separate source substrings, not a continuous code listing. The method signs the literal appid with the timestamp and nonce, then merges the optional sixth-argument header object. This merge happens after signature generation. A caller can override `appid`, but the method does not recompute `clientsign` after that override. Related POST, PUT, synchronous GET, and blob methods also use `Kt`. Another method near offset 3,690,388 embeds `"D1R0m75G"` directly in both `appid` and its `clientsign` input.

The inspected common-wrapper region has one `Kt` assignment, and that assignment is a string literal. This proves a hardcoded default in this deployed web client. It does not prove that every platform client, backend, or future bundle uses the same value.

Earlier anonymous command-line requests to `https://www.zjooc.cn/` and `https://www.zjooc.cn/ucenter/student/course/study/8a221122a079851f01a089ef43b03a72/` returned HTTP 404 on 2026-11-03 at 20:21 and 20:22 UTC. The authorized browser session loaded the student course list and its bundle. The earlier 404s describe those anonymous requests only.

No local project code was used as evidence. The local script's literal does not establish how the platform behaves.

An Internet Archive capture of the 2019 homepage linked `/lano-deploy/manifest.js`, `6.js`, `vendor.js`, and `app.js`, but those JS bodies were not archived. Grok Search refused to locate application identifiers or JavaScript bundles. The current first-party bundle was available from the authorized browser page without credentials.

## Caveats / Not Found

The conclusion applies to the inspected current web bundle. It does not establish behavior for other platform clients, backend services, or future bundles. The GET wrapper permits caller-supplied header overrides, so the literal is a default rather than an immutable value for every call.

The 2019 archive contains no usable JS body. The earlier anonymous 404s do not invalidate the current bundle evidence. No local project code or related spec was used to establish platform behavior.
