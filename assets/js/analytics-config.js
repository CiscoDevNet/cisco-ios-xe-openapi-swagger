/* analytics-config.js — public, non-secret analytics configuration.
 *
 * This is the single place that holds the PostHog project key + host and the
 * app-version / environment overrides. It is loaded before analytics.js on
 * every page (managed by scripts/inject_pwa.py).
 *
 * IMPORTANT — this is NOT a secret store:
 *   - A PostHog *project API key* (starts with "phc_") is a PUBLIC, client-side
 *     write key, exactly like the Microsoft Clarity project id. It can only
 *     capture events; it cannot read data. It is safe to ship to the browser.
 *   - Do NOT put PostHog *personal* API keys (phx_...) or any real secret here.
 *
 * How the value is provided (pick one):
 *   1. Edit the placeholder below directly (simplest for a static site).
 *   2. Replace PLACEHOLDER_POSTHOG_KEY at deploy time via CI
 *      (e.g. `sed -i "s/PLACEHOLDER_POSTHOG_KEY/$POSTHOG_KEY/" assets/js/analytics-config.js`),
 *      reading $POSTHOG_KEY from a CI variable/environment.
 *
 * If the key is empty or still the placeholder, PostHog stays DISABLED and
 * Microsoft Clarity continues to work unchanged (fail-open, never breaks).
 */
window.__ANALYTICS_CONFIG__ = {
  posthog: {
    // PostHog project API key (public write key, "phc_..."). Injected at deploy.
    apiKey: 'phc_oyKEQ3fweMKaM9Hzo8ppJMod3RNNP54zPrRH8HpECPaS',
    // Ingestion host. US cloud: https://us.i.posthog.com | EU: https://eu.i.posthog.com
    host: 'https://us.i.posthog.com'
  },
  // Web-app build version reported as the `app_version` event property.
  // Keep roughly in step with the service-worker CACHE_VERSION on releases.
  appVersion: 'v83-2026.07.17h',
  // Leave blank to auto-detect from the hostname
  // (localhost -> development, CiscoDevNet -> production, jeremycohoe -> staging).
  environment: '',
  // Honor the browser Do-Not-Track signal for BOTH PostHog and Clarity.
  // Set to false to always track (not recommended).
  respectDoNotTrack: true
};
