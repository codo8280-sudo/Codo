# CODO OAuth staging web

Static HTTPS consent UI for the CODO Supabase OAuth 2.1 staging server.

## Security model

- no service-role or secret API key in browser code;
- only the Supabase **publishable** key is present;
- tokens are stored in `sessionStorage`, never `localStorage`;
- no external JavaScript dependency;
- strict CSP;
- no `innerHTML`, `eval` or `document.write`;
- the consent response is accepted only when the redirect matches the registered CODO mobile callback `ci.codo.app:/oauthredirect`;
- the page is excluded from indexing.

## Staging URLs

After GitHub Pages deployment:

```text
Site URL: https://codo8280-sudo.github.io/Codo
Authorization path: /oauth/consent/
Consent URL: https://codo8280-sudo.github.io/Codo/oauth/consent/
```

Supabase Auth concatenates the configured Site URL and Authorization Path.

This surface is staging-only. A production authorization UI must use the final CODO domain and a separate production OAuth client.
