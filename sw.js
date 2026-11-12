/* Service worker do site rafaelmsouza.adv.br: permite instalar como app, funciona com internet fraca
   e recebe os avisos (notificações) da Área do cliente. */
const CACHE = 'rms-site-v1';
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', e => {
  const r = e.request;
  if (r.method !== 'GET' || new URL(r.url).origin !== location.origin) return;
  e.respondWith(fetch(r).then(resp => {
    if (resp.ok && r.mode === 'navigate') { const c = resp.clone(); caches.open(CACHE).then(k => k.put('./', c)) }
    return resp;
  }).catch(() => caches.match(r).then(x => x || caches.match('./'))));
});
self.addEventListener('push', e => {
  let m = {};
  try { m = e.data ? e.data.json() : {} } catch (x) { m = { body: e.data && e.data.text() } }
  e.waitUntil(self.registration.showNotification(m.title || 'Rafael de Mello Souza – Advogado', {
    body: m.body || '', icon: 'icon-192.png', badge: 'icon-192.png', tag: m.tag || 'rms-aviso', data: { url: m.url || '/#consulta' }
  }));
});
self.addEventListener('notificationclick', e => {
  e.notification.close();
  const alvo = new URL((e.notification.data && e.notification.data.url) || '/#consulta', self.registration.scope).href;
  e.waitUntil(self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(L => {
    for (const c of L) if ('focus' in c) { if ('navigate' in c) c.navigate(alvo).catch(() => { }); return c.focus() }
    return self.clients.openWindow(alvo);
  }));
});
