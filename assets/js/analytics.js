/* analytics.js — unified analytics service for the IOS-XE OpenAPI docs site.
 *
 * ONE wrapper that fans every tracked action out to BOTH:
 *   - Microsoft Clarity  -> custom event + custom tags (for heatmaps/session
 *     recordings and debugging). Clarity is bootstrapped separately in
 *     sw-register.js; this file only *uses* window.clarity when present.
 *   - PostHog            -> capture() with normalized properties (for
 *     aggregate reports, charts, dashboards, and exports).
 *
 * Application code should NEVER call window.clarity or window.posthog directly.
 * It calls window.analytics.* (or the legacy window.__iosxeTrack shim, which
 * this file re-points at the same pipeline so existing call sites also reach
 * PostHog).
 *
 * Privacy: sanitize() drops sensitive keys and redacts email/IP-shaped values
 * before anything is sent. Only normalized, non-sensitive metadata leaves the
 * browser. See docs/ANALYTICS.md.
 *
 * Fail-silent everywhere: analytics must never break the page.
 */
(function () {
  'use strict';

  var CFG = (window.__ANALYTICS_CONFIG__ || {});
  var PH = CFG.posthog || {};

  // --- environment + app version --------------------------------------------

  function detectEnv() {
    var h = (location.hostname || '').toLowerCase();
    if (!h || h === 'localhost' || h === '127.0.0.1' || h === '[::1]') return 'development';
    if (h.indexOf('ciscodevnet.github.io') !== -1) return 'production';
    if (h.indexOf('jeremycohoe.github.io') !== -1) return 'staging';
    return 'production';
  }

  var ENV = CFG.environment || detectEnv();
  var APP_VERSION = CFG.appVersion || 'unknown';

  // Honor the browser Do-Not-Track signal (unless the site owner disabled it
  // via CFG.respectDoNotTrack === false). When DNT is on we send NOTHING to
  // PostHog or Clarity from the wrapper, and PostHog is not even loaded.
  function dntEnabled() {
    try {
      if (CFG.respectDoNotTrack === false) return false;
      var d = navigator.doNotTrack || window.doNotTrack || navigator.msDoNotTrack;
      return d === '1' || d === 'yes';
    } catch (e) { return false; }
  }
  var DNT = dntEnabled();

  // Friendly label for the current surface, mirroring sw-register.js. Used as
  // the default `page_or_section` when a caller does not pass one.
  function pageOrSection() {
    try {
      var segs = (location.pathname || '').split('/').filter(Boolean);
      var last = segs.length ? segs[segs.length - 1] : 'index.html';
      var dir = segs.length > 1 ? segs[segs.length - 2] : '';
      if (/^swagger-(.+)-model$/.test(dir)) return 'swagger-viewer';
      if (last === '' || last === 'index.html') return 'hub';
      return last.replace(/\.html?$/i, '');
    } catch (e) { return 'unknown'; }
  }

  // --- privacy: sanitize event properties -----------------------------------
  // Denylist of property KEYS that must never be sent (PII / secrets / raw
  // identifiers). Matching is exact on the lower-cased key so we never drop a
  // benign key by substring accident.
  var DENY_KEYS = {};
  ['email', 'e_mail', 'mail', 'user', 'username', 'user_name', 'name',
   'customer', 'customer_name', 'account', 'password', 'passwd', 'pwd',
   'token', 'secret', 'api_key', 'apikey', 'auth', 'authorization', 'cookie',
   'session_id', 'sessionid', 'ip', 'ip_address', 'ipaddress', 'ipv4', 'ipv6',
   'host', 'hostname', 'fqdn', 'serial', 'serial_number', 'device_id',
   'deviceid', 'mac', 'mac_address', 'url', 'uri', 'href', 'raw_url',
   'payload', 'body', 'request_body', 'response_body', 'query', 'search',
   'search_text', 'q', 'term', 'keyword', 'filter_text'
  ].forEach(function (k) { DENY_KEYS[k] = 1; });

  var EMAIL_RE = /[^\s@]+@[^\s@]+\.[a-z]{2,}/i;
  var IPV4_RE = /\b\d{1,3}(?:\.\d{1,3}){3}\b/;

  function sanitize(props) {
    var out = {};
    if (!props || typeof props !== 'object') return out;
    Object.keys(props).forEach(function (k) {
      if (DENY_KEYS[String(k).toLowerCase()] === 1) return;   // drop PII keys
      var v = props[k];
      if (v == null) return;
      if (typeof v === 'number' || typeof v === 'boolean') { out[k] = v; return; }
      if (typeof v === 'object') return;                      // never send blobs
      v = String(v);
      if (EMAIL_RE.test(v)) return;                           // redact emails
      if (IPV4_RE.test(v)) return;                            // redact IPv4
      if (v.length > 160) v = v.slice(0, 160);                // truncate
      out[k] = v;
    });
    return out;
  }

  // Attach the standard context (app_version, environment, page_or_section)
  // that every event should carry, unless the caller already supplied it.
  function withContext(props) {
    props = sanitize(props);
    if (props.app_version == null) props.app_version = APP_VERSION;
    if (props.environment == null) props.environment = ENV;
    if (props.page_or_section == null) props.page_or_section = pageOrSection();
    if (props.model_category != null) props.model_category = String(props.model_category).toLowerCase();
    return props;
  }

  // --- sinks -----------------------------------------------------------------

  function toClarity(name, props) {
    try {
      if (typeof window.clarity !== 'function') return;
      window.clarity('event', String(name));
      // Mirror the same metadata as Clarity custom tags so recordings can be
      // sliced by the same dimensions used in PostHog.
      Object.keys(props).forEach(function (k) {
        var v = props[k];
        if (v == null || v === '') return;
        try { window.clarity('set', k, String(v)); } catch (e) { /* noop */ }
      });
    } catch (e) { /* noop */ }
  }

  function toPostHog(name, props) {
    try {
      if (window.posthog && typeof window.posthog.capture === 'function') {
        window.posthog.capture(String(name), props);
      }
    } catch (e) { /* noop */ }
  }

  // --- core track ------------------------------------------------------------

  function track(name, props) {
    try {
      if (!name || DNT) return;
      var enriched = withContext(props || {});
      toPostHog(name, enriched);
      toClarity(name, enriched);
    } catch (e) { /* noop */ }
  }

  // --- workflow instrumentation ---------------------------------------------
  // A workflow is a multi-step user goal (build a subscription, generate code).
  // startWorkflow() opens it with a correlation id + start time; completeWorkflow()
  // closes it with status + duration_ms so funnels + drop-off are measurable.
  function _uuid() {
    try { if (window.crypto && typeof crypto.randomUUID === 'function') return crypto.randomUUID(); } catch (e) { /* noop */ }
    return 'wf-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 10);
  }
  function _now() {
    try { return (window.performance && typeof performance.now === 'function') ? performance.now() : Date.now(); }
    catch (e) { return Date.now(); }
  }

  var _openWf = {};   // workflow_id -> { handle, ctx } for abandonment reporting

  function startWorkflow(workflow, context) {
    var handle = { workflow: workflow, workflow_id: _uuid(), _t0: _now() };
    try {
      var props = {};
      if (context) Object.keys(context).forEach(function (k) { props[k] = context[k]; });
      props.workflow = workflow;
      props.workflow_id = handle.workflow_id;
      _openWf[handle.workflow_id] = { handle: handle, ctx: context || {} };
      track('workflow_started', props);
    } catch (e) { /* noop */ }
    return handle;
  }

  function completeWorkflow(handle, outcome) {
    try {
      handle = handle || {};
      outcome = outcome || {};
      if (handle.workflow_id) delete _openWf[handle.workflow_id];
      var props = {};
      Object.keys(outcome).forEach(function (k) {
        if (k === 'status' || k === 'error_type' || k === 'step_count') return;
        props[k] = outcome[k];
      });
      props.workflow = outcome.workflow || handle.workflow;
      if (handle.workflow_id) props.workflow_id = handle.workflow_id;
      props.status = outcome.status || 'success';
      if (handle._t0 != null) props.duration_ms = Math.round(_now() - handle._t0);
      if (outcome.step_count != null) props.step_count = outcome.step_count;
      if (outcome.error_type != null) props.error_type = outcome.error_type;
      track('workflow_completed', props);
    } catch (e) { /* noop */ }
  }

  // Any workflow still open when the page is left is reported abandoned, so the
  // funnel shows real drop-off. pagehide (not visibilitychange) => a tab switch
  // the user returns from is not counted as abandonment.
  function _flushAbandoned() {
    try {
      Object.keys(_openWf).forEach(function (id) {
        var rec = _openWf[id];
        delete _openWf[id];
        if (!rec) return;
        var props = {};
        Object.keys(rec.ctx).forEach(function (k) { props[k] = rec.ctx[k]; });
        props.workflow = rec.handle.workflow;
        props.workflow_id = id;
        props.status = 'abandoned';
        if (rec.handle._t0 != null) props.duration_ms = Math.round(_now() - rec.handle._t0);
        track('workflow_completed', props);
      });
    } catch (e) { /* noop */ }
  }
  try { window.addEventListener('pagehide', _flushAbandoned); } catch (e) { /* noop */ }

  // --- public wrapper --------------------------------------------------------

  var analytics = {
    track: track,

    // The headline event: an API operation was exercised. Matches the agreed
    // call shape exactly:
    //   analytics.trackApiRequest({ api_operation, yang_model, http_code,
    //                               result, page_or_section })
    trackApiRequest: function (d) {
      d = d || {};
      track('api_request', {
        api_operation: d.api_operation,
        yang_model: d.yang_model,
        http_code: d.http_code,
        result: d.result,
        page_or_section: d.page_or_section
      });
    },

    // Named helpers for the standard event set (all optional props).
    trackAppLoaded: function (d) { track('app_loaded', d || {}); },
    trackDataModelSelected: function (d) { track('data_model_selected', d || {}); },
    trackApiOperationSelected: function (d) { track('api_operation_selected', d || {}); },
    trackApiError: function (d) { track('api_error', d || {}); },
    trackExportResults: function (d) { track('export_results', d || {}); },
    trackWorkflowCompleted: function (d) { track('workflow_completed', d || {}); },
    startWorkflow: startWorkflow,
    completeWorkflow: completeWorkflow
  };

  window.analytics = analytics;

  // Legacy shim: existing call sites use window.__iosxeTrack(name, data). Route
  // them through the same pipeline so they now also reach PostHog (they already
  // reached Clarity). This intentionally overrides the Clarity-only definition
  // from sw-register.js (analytics.js loads after it).
  window.__iosxeTrack = function (name, data) { track(name, data); };

  // --- PostHog bootstrap -----------------------------------------------------
  // Official async loader stub: queues calls until static/array.js arrives and
  // replaces window.posthog with the real client (which replays the queue).
  function loadPostHog(key, host) {
    if (DNT) return false;                                        // Do-Not-Track
    if (!key || key.indexOf('PLACEHOLDER') !== -1) return false;  // not configured
    if (window.__iosxePostHogInit) return true;
    window.__iosxePostHogInit = true;
    try {
      !function (t, e) {
        var o, n, p, r;
        e.__SV || (window.posthog = e, e._i = [], e.init = function (i, s, a) {
          function g(t, e) {
            var o = e.split('.');
            2 == o.length && (t = t[o[0]], e = o[1]);
            t[e] = function () { t.push([e].concat(Array.prototype.slice.call(arguments, 0))); };
          }
          (p = t.createElement('script')).type = 'text/javascript';
          p.crossOrigin = 'anonymous';
          p.async = !0;
          p.src = s.api_host.replace('.i.posthog.com', '-assets.i.posthog.com') + '/static/array.js';
          (r = t.getElementsByTagName('script')[0]).parentNode.insertBefore(p, r);
          var u = e;
          for (void 0 !== a ? u = e[a] = [] : a = 'posthog', u.people = u.people || [],
            u.toString = function (t) { var e = 'posthog'; return 'posthog' !== a && (e += '.' + a), t || (e += ' (stub)'), e; },
            u.people.toString = function () { return u.toString(1) + '.people (stub)'; },
            o = 'init capture register register_once register_for_session unregister unregister_for_session getFeatureFlag getFeatureFlagPayload isFeatureEnabled reloadFeatureFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException loadToolbar get_property getSessionProperty createPersonProfile opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing clear_opt_in_out_capturing debug getPageViewId'.split(' '), n = 0; n < o.length; n++) g(u, o[n]);
          e._i.push([i, s, a]);
        }, e.__SV = 1);
      }(document, window.posthog || []);

      window.posthog.init(key, {
        api_host: host || 'https://us.i.posthog.com',
        // Opt into PostHog's current default behaviors (ingestion + payload
        // encoding). Matches the official snippet; without it the current
        // array.js posts a body the server rejects with 401 "without an
        // api_key".
        defaults: '2026-05-30',
        // Clarity handles session recording + click autocapture. PostHog
        // captures our structured events PLUS pageviews (for the Web Analytics
        // dashboard: sessions, unique visitors, top paths). $current_url is
        // still denylisted below, so only page paths ($pathname) are sent -
        // no query strings / hashes.
        autocapture: false,
        capture_pageview: true,
        capture_pageleave: true,
        capture_performance: false,
        disable_session_recording: true,
        disable_surveys: true,
        person_profiles: 'identified_only',
        // Privacy: drop PostHog's auto-captured raw URL + referrer properties.
        // Uses the native property_denylist (a plain array) rather than a
        // sanitize_properties function — a rebuilding function corrupts the
        // payload so the server rejects it with 401 "without an api_key".
        // ($ip is dropped by the project's "Discard client IP data" setting;
        // our own event props are already sanitized in the wrapper.)
        property_denylist: [
          '$current_url', '$initial_current_url',
          '$referrer', '$initial_referrer',
          '$referring_domain', '$initial_referring_domain'
        ]
      });
      return true;
    } catch (e) { return false; }
  }

  loadPostHog(PH.apiKey, PH.host);

  // --- app_loaded (once per page view) ---------------------------------------
  function fireAppLoaded() {
    analytics.trackAppLoaded({});
  }
  if (!DNT) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fireAppLoaded);
    } else {
      fireAppLoaded();
    }
  }
})();
