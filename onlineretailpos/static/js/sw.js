// Service Worker for Ireti POS Light PWA

// Version: 1.1.0 - Enhanced static assets caching (PWA-004)

const CACHE_NAME = 'ireti-pos-v1.1.0';
const STATIC_CACHE = 'static-v1.1.0';
const API_CACHE = 'api-v1.0.0';

// Static assets for cache-first strategy (PWA-004)

const STATIC_CACHE_URLS = [
    '/',
    '/static/css/sb-admin-2.min.css',
    '/static/vendor/fontawesome-free/css/all.min.css',
    '/static/vendor/datatables/dataTables.bootstrap4.min.css',
    '/static/js/sb-admin-2.min.js',
    '/static/vendor/jquery/jquery.min.js',
    '/static/vendor/bootstrap/js/bootstrap.bundle.min.js',
    '/static/vendor/jquery-easing/jquery.easing.min.js',
    '/static/vendor/datatables/jquery.dataTables.min.js',
    '/static/vendor/datatables/dataTables.bootstrap4.min.js',
    '/static/js/demo/datatables-demo.js',
    '/static/vendor/fontawesome-free/webfonts/fa-solid-900.woff2',
    '/static/vendor/fontawesome-free/webfonts/fa-regular-400.woff2',
    '/static/vendor/fontawesome-free/webfonts/fa-brands-400.woff2',
    '/static/img/cash-register-g87e120a86_640.png',
    '/static/img/icons/icon-192x192.png',
    '/static/img/icons/icon-512x512.png',
    '/static/manifest.webmanifest',
    '/offline'
];

// API endpoints for stale-while-revalidate strategy (PWA-005)
const API_ENDPOINTS = [
    '/dashboard/',
    '/api/products/',
    '/api/inventory/',
    '/api/dashboard-data/'
];

// Cache duration in milliseconds (1 hour)
const CACHE_DURATION = 60 * 60 * 1000;

// Install event - cache static assets
self.addEventListener('install', (event) => {
    console.log('[SW] Installing service worker v1.1.0...');
    
    event.waitUntil(
        Promise.all([
            // Cache static assets in separate cache

            // Cache static assets
            caches.open(STATIC_CACHE)
                .then((cache) => {
                    console.log('[SW] Caching static assets');
                    return cache.addAll(STATIC_CACHE_URLS);
                }),
            // Cache core app shell in main cache
            caches.open(CACHE_NAME)
                .then((cache) => {
                    console.log('[SW] Caching app shell');
                    return cache.addAll(['/']);
                })
        ])
        .then(() => {
            console.log('[SW] Service worker installed');

            // Initialize API cache
            caches.open(API_CACHE)
                .then((cache) => {
                    console.log('[SW] Initialized API cache');
                    return cache;
                })
        ])
        .then(() => {
            console.log('[SW] Service worker installed successfully');
            return self.skipWaiting();
        })
        .catch((error) => {
            console.error('[SW] Error during install:', error);
        })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('[SW] Activating service worker v1.1.0...');
    
    const expectedCaches = [CACHE_NAME, STATIC_CACHE, API_CACHE];

    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (!expectedCaches.includes(cacheName)) {
                            console.log('[SW] Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('[SW] Service worker activated successfully');
                return self.clients.claim();
            })
    );
});

// Fetch event - handle network requests with enhanced caching strategies
self.addEventListener('fetch', (event) => {
    // Skip non-GET requests
    if (event.request.method !== 'GET') {
        return;
    }

    // Skip requests with authentication (avoid caching user-specific content)
    if (event.request.url.includes('/staff_portal/') || 
        event.request.url.includes('/user/login/') ||
        event.request.url.includes('/user/logout/') ||
        event.request.url.includes('/admin/') ||
        event.request.url.includes('/csrf_token')) {
        return;
    }

    event.respondWith(
        handleRequest(event.request)
    );
});

// PWA-004 & PWA-005: Enhanced request handling with proper caching strategies
async function handleRequest(request) {
    const url = new URL(request.url);
    
    try {
        // PWA-004: Cache-first strategy for static assets
        if (isStaticAsset(request.url)) {
            return handleStaticAsset(request);
        }
        
        // PWA-005: Stale-while-revalidate for read-only API endpoints
        if (isReadOnlyAPI(request.url)) {
            return handleAPIRequest(request);
        }
        
        // Network-first strategy for navigation and other requests
        return handleNavigation(request);
        
    } catch (error) {
        console.error('[SW] Error handling request:', error);
        return handleOfflineFallback(request);
    }
}

// PWA-004: Handle static assets with cache-first strategy
async function handleStaticAsset(request) {
    const cachedResponse = await caches.match(request, { cacheName: STATIC_CACHE });
    
    if (cachedResponse) {
        console.log('[SW] Serving from static cache:', request.url);
        return cachedResponse;
    }
    
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            const cache = await caches.open(STATIC_CACHE);
            cache.put(request, networkResponse.clone());
            console.log('[SW] Cached static asset:', request.url);
        }
        
        return networkResponse;
    } catch (error) {
        console.error('[SW] Failed to fetch static asset:', request.url);
        throw error;
    }
}

// PWA-005: Handle API requests with stale-while-revalidate
async function handleAPIRequest(request) {
    const cachedResponse = await caches.match(request, { cacheName: API_CACHE });
    
    // Return cached version immediately if available
    if (cachedResponse) {
        console.log('[SW] Serving from API cache:', request.url);
        
        // Revalidate in the background
        fetch(request)
            .then(async (networkResponse) => {
                if (networkResponse.ok) {
                    const cache = await caches.open(API_CACHE);
                    cache.put(request, networkResponse.clone());
                    console.log('[SW] Updated API cache:', request.url);
                }
            })
            .catch((error) => {
                console.log('[SW] Background revalidation failed:', request.url);
            });
        
        return cachedResponse;
    }
    
    // No cached version, fetch from network
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            const cache = await caches.open(API_CACHE);
            cache.put(request, networkResponse.clone());
            console.log('[SW] Cached API response:', request.url);
        }
        
        return networkResponse;
    } catch (error) {
        console.error('[SW] Failed to fetch API:', request.url);
        throw error;
    }
}

// Handle navigation requests with network-first strategy
async function handleNavigation(request) {
    try {
        const networkResponse = await fetch(request);
        return networkResponse;
    } catch (error) {
        // Try cache as fallback
        const cachedResponse = await caches.match(request);
        
        if (cachedResponse) {
            return cachedResponse;
        }
        

        event.request.url.includes('/admin/login/') ||
        event.request.url.includes('/admin/logout/') ||
        event.request.url.includes('csrf')) {
        return;
    }

    const url = new URL(event.request.url);
    
    // Cache-first strategy for static assets (PWA-004)
    if (isStaticAsset(event.request.url)) {
        event.respondWith(cacheFirstStrategy(event.request, STATIC_CACHE));
    }
    // Stale-while-revalidate for API endpoints (PWA-005) 
    else if (isAPIEndpoint(url.pathname)) {
        event.respondWith(staleWhileRevalidateStrategy(event.request, API_CACHE));
    }
    // Network-first with offline fallback for navigation
    else {
        event.respondWith(networkFirstStrategy(event.request));
    }
});

// Cache-first strategy for static assets (PWA-004)
async function cacheFirstStrategy(request, cacheName) {
    try {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            // Check if cached resource supports cache-busting via URL hash/version
            const url = new URL(request.url);
            const hasVersion = url.search.includes('v=') || url.pathname.includes('.min.');
            
            if (hasVersion) {
                return cachedResponse;
            }
        }

        // Fetch from network and cache
        const networkResponse = await fetch(request);
        if (networkResponse && networkResponse.status === 200) {
            const cache = await caches.open(cacheName);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.log('[SW] Cache-first fallback for:', request.url);
        const cachedResponse = await caches.match(request);
        return cachedResponse || new Response('Offline', { status: 503 });
    }
}

// Stale-while-revalidate strategy for API endpoints (PWA-005)
async function staleWhileRevalidateStrategy(request, cacheName) {
    try {
        const cache = await caches.open(cacheName);
        const cachedResponse = await cache.match(request);
        
        // Fetch from network and update cache in background
        const networkResponsePromise = fetch(request)
            .then(response => {
                if (response && response.status === 200) {
                    // Add timestamp for cache expiration
                    const responseToCache = response.clone();
                    const headers = new Headers(responseToCache.headers);
                    headers.set('sw-cached-at', Date.now().toString());
                    
                    const modifiedResponse = new Response(responseToCache.body, {
                        status: responseToCache.status,
                        statusText: responseToCache.statusText,
                        headers: headers
                    });
                    
                    cache.put(request, modifiedResponse);
                }
                return response;
            })
            .catch(error => {
                console.log('[SW] Network error for API:', request.url, error);
                return null;
            });

        // Return cached response immediately if available, otherwise wait for network
        if (cachedResponse) {
            // Check if cache is expired (1 hour)
            const cachedAt = cachedResponse.headers.get('sw-cached-at');
            const isExpired = cachedAt && (Date.now() - parseInt(cachedAt)) > CACHE_DURATION;
            
            if (!isExpired) {
                // Return cached response, update in background
                networkResponsePromise.catch(() => {}); // Prevent unhandled rejection
                return cachedResponse;
            }
        }

        // Wait for network response if no cache or expired
        return await networkResponsePromise || cachedResponse || 
               new Response('{"error": "Offline"}', { 
                   status: 503, 
                   headers: { 'Content-Type': 'application/json' }
               });
    } catch (error) {
        console.error('[SW] Stale-while-revalidate error:', error);
        return new Response('{"error": "Service error"}', { 
            status: 503, 
            headers: { 'Content-Type': 'application/json' }
        });
    }
}

// Network-first strategy with offline fallback
async function networkFirstStrategy(request) {
    try {
        const networkResponse = await fetch(request);
        return networkResponse;
    } catch (error) {
        console.log('[SW] Network-first fallback for:', request.url);
        
        // Try cache first
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }

        // For navigation requests, return offline page
        if (request.mode === 'navigate') {
            return caches.match('/offline');
        }
        
        throw error;
    }
}

// Handle offline fallbacks
async function handleOfflineFallback(request) {
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
        return cachedResponse;
    }
    
    // For navigation requests, return offline page
    if (request.mode === 'navigate') {
        return caches.match('/offline');
    }
    
    // For other requests, return a generic offline response
    return new Response('Offline', {
        status: 503,
        statusText: 'Service Unavailable'
    });

        // For other requests, return a generic offline response
        return new Response('Offline', {
            status: 503,
            statusText: 'Service Unavailable'
        });
    }
}

// Helper function to determine if a URL is a static asset
function isStaticAsset(url) {
    return url.includes('/static/') || 
           url.includes('/manifest.webmanifest') ||
           url.includes('/favicon.ico') ||
           url.endsWith('.css') ||
           url.endsWith('.js') ||
           url.endsWith('.png') ||
           url.endsWith('.jpg') ||
           url.endsWith('.svg') ||
           url.endsWith('.woff') ||
           url.endsWith('.woff2');
}

// Helper function to determine if a URL is an API endpoint (PWA-005)
function isAPIEndpoint(pathname) {
    return API_ENDPOINTS.some(endpoint => pathname.startsWith(endpoint)) ||
           pathname.includes('/api/') ||
           (pathname.includes('/dashboard') && !pathname.includes('/admin/'));
}

// PWA-005: Helper function to identify read-only API endpoints safe for caching
function isReadOnlyAPI(url) {
    // Cache dashboard and product lookup endpoints (read-only GET requests)
    const readOnlyPatterns = [
        '/dashboard_sales',
        '/dashboard_department', 
        '/dashboard_products',
        '/product_lookup',
        '/api/products',
        '/api/inventory'
    ];
    
    return readOnlyPatterns.some(pattern => url.includes(pattern));
}


// Handle messages from the main thread (PWA-016: Update flow)
self.addEventListener('message', (event) => {
    console.log('[SW] Received message:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        console.log('[SW] Received SKIP_WAITING message');
        console.log('[SW] Skipping waiting and claiming clients');
        self.skipWaiting();
        self.clients.claim();
        
        // Notify all clients that update is complete
        self.clients.matchAll().then(clients => {
            clients.forEach(client => {
                client.postMessage({ type: 'SW_UPDATED' });
            });
        });
    }
    
    if (event.data && event.data.type === 'GET_VERSION') {
        event.ports[0].postMessage({ version: '1.1.0' });
    }
    
    // PWA-016: Handle version requests
    if (event.data && event.data.type === 'GET_VERSION') {
        event.ports[0].postMessage({
            type: 'VERSION_INFO',
            version: '1.1.0'
        });
    }
});

// PWA-016: Service Worker Update Flow
// Send update available message to all clients
function notifyClientsAboutUpdate() {
    self.clients.matchAll().then(clients => {
        clients.forEach(client => {
            client.postMessage({
                type: 'UPDATE_AVAILABLE'
            });
        });
    });
}

// Notify clients when this SW becomes the waiting SW
if (self.registration.waiting) {
    notifyClientsAboutUpdate();
}
});

// Notify clients when a new service worker is waiting (PWA-016)
self.addEventListener('waiting', (event) => {
    console.log('[SW] New service worker is waiting');
    self.clients.matchAll().then(clients => {
        clients.forEach(client => {
            client.postMessage({ type: 'SW_WAITING' });
        });
    });
});

// Notify clients when service worker updates (PWA-016)
self.addEventListener('updatefound', (event) => {
    console.log('[SW] Service worker update found');
    self.clients.matchAll().then(clients => {
        clients.forEach(client => {
            client.postMessage({ type: 'SW_UPDATE_FOUND' });
        });
    });
});
