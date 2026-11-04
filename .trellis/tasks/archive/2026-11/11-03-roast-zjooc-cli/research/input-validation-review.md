# Input validation review

## Decision

Relax checks that reject usable credentials or discarded URL details.
Keep checks that determine outgoing credential scope, required identifiers, valid syntax, and private diagnostics.
This is a read-only assessment. It changes no application, test, spec, or README file.

## Findings

### P1: Unrelated cookies block a usable export

Location: `src/roast_zjooc/cli.py:283` and `src/roast_zjooc/cli.py:288`.

A JSON export with a valid `.zjooc.cn` cookie and an unrelated `.example.org` cookie fails before client construction.
The unrelated cookie does not prevent the valid cookie from working.
A native `httpx` request with both scoped cookies sends only `sid=synthetic` to `www.zjooc.cn`.

Recommendation: ignore cookies outside the target domain scope instead of rejecting the entire export.
Retain each accepted cookie's actual domain. Never widen an unrelated cookie to `.zjooc.cn`.
Reject a result with no usable credentials.

### P2: Browser-only metadata blocks HTTP credentials

Location: `src/roast_zjooc/cli.py:296` and `src/roast_zjooc/cli.py:326`.

`[{"name":"sid","value":"synthetic","httpOnly":0}]` fails because `httpOnly` must be a JSON boolean.
This field controls browser script access. It does not determine this CLI's outgoing Cookie header.
Native cookie records with and without the `HttpOnly` attribute both produce `sid=synthetic`.

Recommendation: do not block this HTTP client on `httpOnly` metadata.
Retain the checks for flags that change transport or scope, including `secure` and `hostOnly`.
Do not treat the string `"false"` as a false value through generic truth conversion.

### P2: Harmless header formatting fails

Location: `src/roast_zjooc/cli.py:254` through the validation at `src/roast_zjooc/cli.py:259`.

`sid=synthetic;` fails on its final empty segment. `sid =synthetic` fails on the space after the name.
Both fail before client construction.
The standard-library `SimpleCookie` parser reads both as the same `sid` value.
Native `httpx` also accepts both strings as header content during request construction.

Recommendation: ignore empty separator segments and trim separator whitespace from the name before validation.
Preserve actual value bytes and later equals signs.
Continue to reject a nonempty segment without an equals sign and names that cannot form a Cookie pair.

Quoted values with spaces also pass native header construction but fail the current CLI check.
Server interpretation has not been established for that case. Header construction alone does not justify general value relaxation.

### P2: Session cookies validate an unused expiry

Location: `src/roast_zjooc/cli.py:299` and `src/roast_zjooc/cli.py:307`.

`{"name":"sid","value":"synthetic","session":true,"expires":"unused"}` fails during expiry conversion.
The same branch discards expiry whenever `session` is true.
The field cannot affect the resulting session cookie, but conversion still blocks it.

Recommendation: resolve an explicit session cookie before expiry conversion.
Continue to validate and preserve expiry for persistent cookies. Do not silently replace invalid persistent expiry values.

### P2: Discarded URL origin details block a usable course identifier

Location: `src/roast_zjooc/cli.py:195`, `src/roast_zjooc/cli.py:211`, and `src/roast_zjooc/cli.py:332`.

The parser rejects HTTP input, a missing scheme, or port 8443 despite a recognizable course path.
The implementation subsequently discards the input origin and constructs a fixed HTTPS URL from the course identifier.
The HTTP client also has a fixed ZJOOC origin.

The main session's native MockTransport probe observed three requests and exit 0 for the canonical input.
Those requests used the fixed host and canonical Referer.
HTTP, missing-scheme, and port-8443 variants each produced exit 1 and no requests.

Recommendation: require a recoverable course identifier, then normalize to the existing fixed outgoing origin.
Keep the observed identifier shape. Fail when no identifier can be extracted.
The input URL must never redirect credentials to an arbitrary destination.

## Checks that must remain

- Keep exactly `--url`, `--cookies`, and `--verbose`/`-v` as requested.
- Keep single-line interactive file/header input. Do not accept raw JSON through the terminal.
- Retain all three JSON file formats and reject corrupt JSON without a header fallback.
- Preserve accepted cookie domain, path, persistent expiry, secure behavior, and host scope.
- Reject CR/LF inside cookie names or values and malformed nonempty header pairs.
- Keep hidden terminal input, hidden traceback locals, sanitized sensitive errors, and safe original decode evidence.
- Keep a fixed outgoing HTTPS destination and authentication failure handling.

Header validation and shared JSON validation cover different input paths.
Removing shared name/value checks merely because the header path already checks them would weaken JSON handling.
No new helper, class, or validation layer is needed for these corrections.

## Test implications

`tests/test_roast_zjooc.py:549` rejects input containing only a foreign-domain cookie.
That case remains valid after filtering because no usable credential remains.
No current test establishes the mixed-domain export contract. An authorized correction should check that only accepted scoped cookies reach the native request.

`tests/test_roast_zjooc.py:574` through its URL cases enforce the discarded origin restrictions.
Narrow those cases if URL normalization is authorized. Retain failure cases for missing or invalid course identifiers.

The existing malformed-pair, raw JSON terminal, private-error, cookie-property, and persistent-expiry checks remain relevant.
No current test requires rejection of `httpOnly=0`, trailing separators, separator whitespace, or unused session expiry text.

## Evidence and limits

The reviewer ran synthetic probes at the current CLI, native `httpx` request constructor, cookie jar, and standard-library Cookie parser.
CLI probes used patched file reads with synthetic JSON and did not read credential files.
No probe sent a network request. No live account, browser, credential store, or source file changed.
Python probes used the current uv environment with `PYTHONDONTWRITEBYTECODE=1`.
The main session supplied the separate URL probe evidence. No application suite rerun was needed for this assessment.
