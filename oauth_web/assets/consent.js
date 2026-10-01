(() => {
  'use strict';

  const SUPABASE_URL = 'https://evchtqxpthfaekpaeibh.supabase.co';
  const PUBLISHABLE_KEY = 'sb_publishable_wei4R0yLkm4Jc9QPt3wMGA_lXM94A27';
  const AUTH_BASE = SUPABASE_URL + '/auth/v1';
  const SESSION_KEY = 'codo.oauth.session.v1';
  const ALLOWED_REDIRECT_PREFIXES = ['ci.codo.app:/oauthredirect'];

  const views = {
    loading: document.getElementById('loading-view'),
    login: document.getElementById('login-view'),
    consent: document.getElementById('consent-view'),
    error: document.getElementById('error-view'),
  };

  const scopeLabels = {
    openid: 'Confirmer votre identité CODO',
    profile: 'Lire les informations de profil de base',
    email: 'Lire votre adresse e-mail',
    phone: 'Lire votre numéro de téléphone',
    offline_access: 'Maintenir la session via un jeton de renouvellement',
  };

  let authorizationId = '';
  let expectedRedirectUri = '';

  function show(name) {
    Object.entries(views).forEach(([key, node]) => {
      node.classList.toggle('hidden', key !== name);
    });
  }

  function setText(id, value) {
    const node = document.getElementById(id);
    if (node) node.textContent = value || '—';
  }

  function showMessage(id, message) {
    const node = document.getElementById(id);
    if (!node) return;
    node.textContent = message;
    node.classList.toggle('hidden', !message);
  }

  function errorMessage(payload, fallback) {
    if (!payload || typeof payload !== 'object') return fallback;
    return payload.msg || payload.message || payload.error_description || payload.error || fallback;
  }

  function authHeaders(accessToken) {
    const headers = {
      apikey: PUBLISHABLE_KEY,
      'Content-Type': 'application/json',
      'X-Client-Info': 'codo-staging-oauth-ui/0.1',
    };
    if (accessToken) headers.Authorization = 'Bearer ' + accessToken;
    return headers;
  }

  async function authFetch(path, options = {}) {
    const response = await fetch(AUTH_BASE + path, {
      ...options,
      headers: {
        ...authHeaders(options.accessToken),
        ...(options.headers || {}),
      },
      cache: 'no-store',
      credentials: 'omit',
      referrerPolicy: 'no-referrer',
    });
    const text = await response.text();
    let payload = null;
    if (text) {
      try { payload = JSON.parse(text); } catch (_) { payload = { message: text }; }
    }
    if (!response.ok) {
      const error = new Error(errorMessage(payload, 'La requête d’authentification a échoué.'));
      error.status = response.status;
      error.payload = payload;
      throw error;
    }
    return payload;
  }

  function readSession() {
    try {
      const raw = sessionStorage.getItem(SESSION_KEY);
      if (!raw) return null;
      const value = JSON.parse(raw);
      if (!value || !value.access_token || !value.refresh_token) return null;
      return value;
    } catch (_) {
      sessionStorage.removeItem(SESSION_KEY);
      return null;
    }
  }

  function saveSession(payload) {
    if (!payload || !payload.access_token || !payload.refresh_token) {
      throw new Error('Session Supabase incomplète.');
    }
    const session = {
      access_token: payload.access_token,
      refresh_token: payload.refresh_token,
      expires_at_ms: Date.now() + Math.max(60, Number(payload.expires_in || 3600) - 30) * 1000,
    };
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(session));
    return session;
  }

  async function refreshSession(session) {
    const payload = await authFetch('/token?grant_type=refresh_token', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: session.refresh_token }),
    });
    return saveSession(payload);
  }

  async function getCurrentUser(session) {
    return await authFetch('/user', {
      method: 'GET',
      accessToken: session.access_token,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  async function ensureSession() {
    let session = readSession();
    if (!session) return null;

    if (Date.now() >= Number(session.expires_at_ms || 0)) {
      try {
        session = await refreshSession(session);
      } catch (_) {
        sessionStorage.removeItem(SESSION_KEY);
        return null;
      }
    }

    try {
      const user = await getCurrentUser(session);
      return { session, user };
    } catch (error) {
      if (error.status !== 401) {
        throw error;
      }
      try {
        session = await refreshSession(session);
        const user = await getCurrentUser(session);
        return { session, user };
      } catch (_) {
        sessionStorage.removeItem(SESSION_KEY);
        return null;
      }
    }
  }

  async function signIn() {
    showMessage('login-error', '');
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const button = document.getElementById('login-button');

    if (!email || !password) {
      showMessage('login-error', 'Renseignez votre e-mail et votre mot de passe.');
      return;
    }

    button.disabled = true;
    try {
      const payload = await authFetch('/token?grant_type=password', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      saveSession(payload);
      document.getElementById('password').value = '';
      await loadAuthorization();
    } catch (error) {
      showMessage('login-error', error.message || 'Connexion impossible.');
    } finally {
      button.disabled = false;
    }
  }

  function isAllowedRedirect(url) {
    return ALLOWED_REDIRECT_PREFIXES.some((prefix) =>
      url === prefix || url.startsWith(prefix + '?') || url.startsWith(prefix + '#')
    );
  }

  function redirectSafely(url) {
    if (!url || typeof url !== 'string') {
      throw new Error('URL de redirection OAuth absente.');
    }

    if (expectedRedirectUri) {
      const exact = url === expectedRedirectUri;
      const withQuery = url.startsWith(expectedRedirectUri + '?');
      const withFragment = url.startsWith(expectedRedirectUri + '#');
      if (!exact && !withQuery && !withFragment) {
        throw new Error('La redirection retournée ne correspond pas au client enregistré.');
      }
    } else if (!isAllowedRedirect(url)) {
      throw new Error('La redirection OAuth retournée n’est pas autorisée en staging.');
    }

    window.location.assign(url);
  }

  function renderScopes(scope) {
    const list = document.getElementById('scope-list');
    while (list.firstChild) list.removeChild(list.firstChild);
    const scopes = String(scope || '')
      .split(/\s+/)
      .map((value) => value.trim())
      .filter(Boolean);
    const values = scopes.length ? scopes : ['email'];

    values.forEach((item) => {
      const li = document.createElement('li');
      li.textContent = scopeLabels[item] || ('Permission OAuth : ' + item);
      list.appendChild(li);
    });
  }

  async function fetchAuthorizationDetails(session) {
    return await authFetch('/oauth/authorizations/' + encodeURIComponent(authorizationId), {
      method: 'GET',
      accessToken: session.access_token,
    });
  }

  async function loadAuthorization() {
    show('loading');
    showMessage('consent-error', '');

    const authenticated = await ensureSession();
    if (!authenticated) {
      show('login');
      return;
    }

    try {
      const details = await fetchAuthorizationDetails(authenticated.session);

      if (details && details.redirect_url && !details.authorization_id) {
        expectedRedirectUri = '';
        redirectSafely(details.redirect_url);
        return;
      }

      if (!details || details.authorization_id !== authorizationId) {
        throw new Error('La demande OAuth retournée est incohérente.');
      }

      expectedRedirectUri = String(details.redirect_uri || '');
      setText('client-name', details.client && details.client.name ? details.client.name : 'Application CODO');
      setText('user-email', details.user && details.user.email ? details.user.email : authenticated.user.email);
      setText('redirect-uri', expectedRedirectUri);
      renderScopes(details.scope);
      show('consent');
    } catch (error) {
      if (error.status === 401) {
        sessionStorage.removeItem(SESSION_KEY);
        show('login');
        return;
      }
      setText('fatal-error', error.message || 'La demande OAuth ne peut pas être chargée.');
      show('error');
    }
  }

  async function decide(action) {
    showMessage('consent-error', '');
    const approve = document.getElementById('approve-button');
    const deny = document.getElementById('deny-button');
    approve.disabled = true;
    deny.disabled = true;

    try {
      const authenticated = await ensureSession();
      if (!authenticated) {
        show('login');
        return;
      }

      const latest = await fetchAuthorizationDetails(authenticated.session);
      if (latest && latest.redirect_url && !latest.authorization_id) {
        expectedRedirectUri = '';
        redirectSafely(latest.redirect_url);
        return;
      }
      if (!latest || latest.authorization_id !== authorizationId) {
        throw new Error('La demande OAuth a changé ou a expiré.');
      }
      expectedRedirectUri = String(latest.redirect_uri || '');

      const result = await authFetch('/oauth/authorizations/' + encodeURIComponent(authorizationId) + '/consent', {
        method: 'POST',
        accessToken: authenticated.session.access_token,
        body: JSON.stringify({ action }),
      });
      redirectSafely(result && result.redirect_url);
    } catch (error) {
      showMessage('consent-error', error.message || 'Impossible d’enregistrer votre décision.');
    } finally {
      approve.disabled = false;
      deny.disabled = false;
    }
  }

  async function signOut() {
    const current = readSession();
    try {
      if (current) {
        await authFetch('/logout?scope=local', {
          method: 'POST',
          accessToken: current.access_token,
          body: JSON.stringify({}),
        });
      }
    } catch (_) {
      // Local session removal is authoritative for this staging UI.
    } finally {
      sessionStorage.removeItem(SESSION_KEY);
      expectedRedirectUri = '';
      show('login');
    }
  }

  function validateAuthorizationId(value) {
    return /^[A-Za-z0-9_-]{8,256}$/.test(value);
  }

  async function init() {
    const params = new URLSearchParams(window.location.search);
    authorizationId = String(params.get('authorization_id') || '').trim();

    if (!validateAuthorizationId(authorizationId)) {
      setText('fatal-error', 'Identifiant d’autorisation absent ou invalide.');
      show('error');
      return;
    }

    document.getElementById('login-button').addEventListener('click', signIn);
    document.getElementById('password').addEventListener('keydown', (event) => {
      if (event.key === 'Enter') signIn();
    });
    document.getElementById('approve-button').addEventListener('click', () => decide('approve'));
    document.getElementById('deny-button').addEventListener('click', () => decide('deny'));
    document.getElementById('logout-button').addEventListener('click', signOut);
    document.getElementById('retry-button').addEventListener('click', loadAuthorization);

    await loadAuthorization();
  }

  init().catch((error) => {
    setText('fatal-error', error && error.message ? error.message : 'Erreur inattendue.');
    show('error');
  });
})();
