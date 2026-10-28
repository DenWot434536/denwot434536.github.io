(() => {
  const COUNTER_ID = 113844022;
  const STORAGE_KEY = 'lozhka.analytics-consent.v1';
  const DISABLE_KEY = `disableYaCounter${COUNTER_ID}`;
  const TAG_URL = `https://mc.yandex.ru/metrika/tag.js?id=${COUNTER_ID}`;
  const banner = document.querySelector('#consent-banner');
  const acceptButton = document.querySelector('[data-consent-accept]');
  const denyButton = document.querySelector('[data-consent-deny]');
  if (!banner || !acceptButton || !denyButton) return;

  let counterActive = false;
  let opener = null;

  // Treat inaccessible or read-only storage as no stored consent. This avoids
  // accidentally reusing an old approval if a later refusal cannot be saved.
  function readChoice() {
    try {
      const probe = `${STORAGE_KEY}.probe`;
      window.localStorage.setItem(probe, '1');
      window.localStorage.removeItem(probe);
      const value = window.localStorage.getItem(STORAGE_KEY);
      return value === 'accepted' || value === 'declined' ? value : null;
    } catch (_error) {
      return null;
    }
  }

  function saveChoice(value) {
    try {
      window.localStorage.setItem(STORAGE_KEY, value);
    } catch (_error) {
      // The choice still applies to this page; the next page will ask again.
    }
  }

  function enableCounter() {
    if (counterActive) return;
    window[DISABLE_KEY] = false;
    if (typeof window.ym !== 'function') {
      window.ym = function () {
        (window.ym.a = window.ym.a || []).push(arguments);
      };
      window.ym.l = Date.now();
    }
    if (![...document.scripts].some((script) => script.src === TAG_URL)) {
      const script = document.createElement('script');
      script.async = true;
      script.src = TAG_URL;
      document.head.appendChild(script);
    }
    window.ym(COUNTER_ID, 'init', {
      ssr: true,
      webvisor: true,
      clickmap: true,
      ecommerce: 'dataLayer',
      referrer: document.referrer,
      url: window.location.href,
      accurateTrackBounce: true,
      trackLinks: true,
    });
    counterActive = true;
  }

  function disableCounter() {
    window[DISABLE_KEY] = true;
    if (counterActive && typeof window.ym === 'function') {
      // The official destruct method stops an already initialized counter.
      window.ym(COUNTER_ID, 'destruct');
    }
    counterActive = false;
  }

  function showSettings(focusTitle = false) {
    banner.hidden = false;
    if (focusTitle) document.querySelector('#consent-title')?.focus();
  }

  function closeSettings() {
    banner.hidden = true;
    if (opener && opener.isConnected) opener.focus();
    opener = null;
  }

  function choose(value) {
    saveChoice(value);
    if (value === 'accepted') enableCounter();
    else disableCounter();
    closeSettings();
  }

  acceptButton.addEventListener('click', () => choose('accepted'));
  denyButton.addEventListener('click', () => choose('declined'));
  document.querySelectorAll('[data-consent-open]').forEach((button) => {
    button.addEventListener('click', () => {
      opener = button;
      showSettings(true);
    });
  });

  // Keep the choice consistent when it is changed in another tab.
  window.addEventListener('storage', (event) => {
    if (event.key !== STORAGE_KEY && event.key !== null) return;
    const choice = readChoice();
    if (choice === 'accepted') {
      enableCounter();
      closeSettings();
    } else {
      disableCounter();
      if (choice === 'declined') closeSettings();
      else showSettings();
    }
  });

  const choice = readChoice();
  if (choice === 'accepted') enableCounter();
  else {
    disableCounter();
    if (choice === null) showSettings();
  }
})();
