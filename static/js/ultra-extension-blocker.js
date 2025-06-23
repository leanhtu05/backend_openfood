/**
 * 🚫 ULTRA Extension Blocker - Maximum strength extension blocking
 * Blocks ALL extension interference immediately
 * Version 3.0 - Ultimate blocking for admin panel
 */

(function() {
    'use strict';
    
    console.log('🚫 ULTRA Extension Blocker v3.0: MAXIMUM BLOCKING ACTIVE');
    
    // IMMEDIATE: Block ALL console methods first
    const originalConsole = {
        error: console.error,
        warn: console.warn,
        log: console.log,
        info: console.info,
        debug: console.debug
    };
    
    // Ultra comprehensive keyword list
    const BLOCK_PATTERNS = [
        // Extension URLs
        'chrome-extension://', 'moz-extension://', 'safari-extension://',
        
        // Runtime errors
        'runtime.lasterror', 'unchecked runtime.lasterror',
        'runtime.lastError', 'Unchecked runtime.lastError',
        
        // Message channel errors
        'message channel closed', 'message channel is closed',
        'listener indicated an asynchronous response',
        'listener indicated', 'asynchronous response',
        
        // Background page errors
        'background page', 'you do not have a background page',
        'You do not have a background page',
        
        // Extension adapter errors
        'extensionadapter', 'extensionAdapter',
        'sendmessagetotab', 'sendMessageToTab',
        'invalid arguments to extensionadapter',
        'invalid arguments to extensionAdapter',
        
        // Cache errors
        'back/forward cache', 'extension port',
        'The page keeping the extension port is moved into back/forward cache',
        
        // Content script errors
        'contentscript.js', 'contentScript.js',
        'inlineform.html', 'inlineForm.html',
        
        // i18next errors
        'i18next', 'languagechanged', 'initialized object',
        
        // Generic patterns
        'error in event handler', '<url>', '<URL>',
        'event handler: error: invalid arguments'
    ];
    
    function isExtensionRelated(message) {
        if (!message) return false;
        const msgLower = message.toString().toLowerCase();
        return BLOCK_PATTERNS.some(pattern => msgLower.includes(pattern.toLowerCase()));
    }
    
    // Override ALL console methods immediately
    console.error = function(...args) {
        const message = args.join(' ');
        if (isExtensionRelated(message)) {
            return; // Complete suppression
        }
        return originalConsole.error.apply(console, args);
    };
    
    console.warn = function(...args) {
        const message = args.join(' ');
        if (isExtensionRelated(message)) {
            return; // Complete suppression
        }
        return originalConsole.warn.apply(console, args);
    };
    
    console.log = function(...args) {
        const message = args.join(' ');
        if (isExtensionRelated(message)) {
            return; // Complete suppression
        }
        return originalConsole.log.apply(console, args);
    };
    
    console.info = function(...args) {
        const message = args.join(' ');
        if (isExtensionRelated(message)) {
            return; // Complete suppression
        }
        return originalConsole.info.apply(console, args);
    };
    
    console.debug = function(...args) {
        const message = args.join(' ');
        if (isExtensionRelated(message)) {
            return; // Complete suppression
        }
        return originalConsole.debug.apply(console, args);
    };
    
    // IMMEDIATE: Block ALL error events
    window.addEventListener('error', function(e) {
        const message = e.message || '';
        const filename = e.filename || '';
        const source = e.source || '';
        
        if (isExtensionRelated(message) || 
            isExtensionRelated(filename) || 
            isExtensionRelated(source)) {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            return false;
        }
    }, true);
    
    // IMMEDIATE: Block ALL promise rejections
    window.addEventListener('unhandledrejection', function(e) {
        const reason = e.reason ? e.reason.toString() : '';
        if (isExtensionRelated(reason)) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }
    }, true);
    
    // IMMEDIATE: Block extension message listeners
    const originalAddEventListener = EventTarget.prototype.addEventListener;
    EventTarget.prototype.addEventListener = function(type, listener, options) {
        if (type === 'message' && listener) {
            const listenerStr = listener.toString();
            if (isExtensionRelated(listenerStr)) {
                return; // Block extension message listeners
            }
        }
        return originalAddEventListener.call(this, type, listener, options);
    };
    
    // IMMEDIATE: Block extension fetch requests
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {
        if (typeof url === 'string' && isExtensionRelated(url)) {
            return Promise.reject(new Error('Extension request blocked'));
        }
        return originalFetch.apply(this, arguments);
    };
    
    // IMMEDIATE: Block extension XHR requests
    const originalXHROpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url) {
        if (typeof url === 'string' && isExtensionRelated(url)) {
            return;
        }
        return originalXHROpen.apply(this, arguments);
    };
    
    // IMMEDIATE: Block chrome runtime access
    if (typeof chrome !== 'undefined' && chrome.runtime) {
        try {
            Object.defineProperty(chrome.runtime, 'sendMessage', {
                value: function() {
                    return Promise.reject(new Error('Extension API blocked'));
                },
                writable: false
            });
        } catch (e) {
            // Ignore if can't override
        }
    }
    
    // IMMEDIATE: DOM cleanup
    function ultraCleanup() {
        const selectors = [
            '[id*="extension"]', '[class*="extension"]',
            '[id*="chrome-extension"]', '[class*="chrome-extension"]',
            'iframe[src*="chrome-extension"]', 'iframe[src*="moz-extension"]',
            '[data-extension]', '[id*="inlineForm"]', '[class*="inlineForm"]',
            'script[src*="chrome-extension"]', 'script[src*="moz-extension"]'
        ];
        
        selectors.forEach(selector => {
            try {
                const elements = document.querySelectorAll(selector);
                elements.forEach(el => el.remove());
            } catch (e) {
                // Ignore selector errors
            }
        });
    }
    
    // Run cleanup immediately and periodically
    ultraCleanup();
    setInterval(ultraCleanup, 1000); // Every second
    
    // DOM observer for real-time blocking
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) {
                    const src = node.src || '';
                    const id = node.id || '';
                    const className = node.className || '';
                    
                    if (isExtensionRelated(src) || 
                        isExtensionRelated(id) || 
                        isExtensionRelated(className)) {
                        node.remove();
                    }
                }
            });
        });
    });
    
    if (document.body) {
        observer.observe(document.body, { 
            childList: true, 
            subtree: true,
            attributes: true
        });
    } else {
        document.addEventListener('DOMContentLoaded', function() {
            observer.observe(document.body, { 
                childList: true, 
                subtree: true,
                attributes: true
            });
        });
    }
    
    console.log('✅ ULTRA Extension Blocker v3.0: MAXIMUM BLOCKING INITIALIZED');
    
    // Export for debugging
    window.UltraExtensionBlocker = {
        isExtensionRelated,
        ultraCleanup,
        observer,
        version: '3.0'
    };
    
})();
