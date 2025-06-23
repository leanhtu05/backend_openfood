/**
 * 🚫 ULTRA Extension Blocker - Comprehensive browser extension interference blocking
 * Blocks all extension errors, warnings, and DOM manipulation
 * Version 2.0 - Enhanced blocking for admin panel
 */

(function() {
    'use strict';

    console.log('🚫 ULTRA Extension Blocker v2.0: Initializing comprehensive blocking...');
    
    // List of extension-related keywords to block (enhanced v2)
    const EXTENSION_KEYWORDS = [
        'chrome-extension://',
        'moz-extension://',
        'safari-extension://',
        'runtime.lastError',
        'runtime.lasterror',
        'message channel closed',
        'listener indicated an asynchronous response',
        'listener indicated',
        'background page',
        'extensionAdapter',
        'extensionadapter',
        'sendMessageToTab',
        'sendmessagetotab',
        'inlineForm.html',
        'inlineform.html',
        'invalid arguments to extensionAdapter',
        'invalid arguments to extensionadapter',
        'You do not have a background page',
        'you do not have a background page',
        'Error in event handler: Error: invalid arguments',
        'error in event handler',
        'Unchecked runtime.lastError',
        'unchecked runtime.lasterror',
        'The page keeping the extension port is moved into back/forward cache',
        'back/forward cache',
        'extension port',
        'contentScript.js',
        'contentscript.js',
        'i18next: languageChanged',
        'i18next: initialized',
        'i18next',
        '<URL>',
        '<url>'
    ];
    
    // Check if message contains extension keywords
    function isExtensionRelated(message) {
        if (!message) return false;
        const msgStr = message.toString().toLowerCase();
        return EXTENSION_KEYWORDS.some(keyword => msgStr.includes(keyword.toLowerCase()));
    }
    
    // Stats tracking
    let stats = {
        blockedErrors: 0,
        blockedPromises: 0,
        blockedRequests: 0,
        removedElements: 0
    };

    // 1. Block window errors
    window.addEventListener('error', function(e) {
        const message = e.message || '';
        const filename = e.filename || '';

        if (isExtensionRelated(message) || isExtensionRelated(filename)) {
            stats.blockedErrors++;
            console.log('🚫 Blocked extension error #' + stats.blockedErrors + ':', message);
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            return false;
        }
    }, true);
    
    // 2. Block unhandled promise rejections
    window.addEventListener('unhandledrejection', function(e) {
        const reason = e.reason ? e.reason.toString() : '';

        if (isExtensionRelated(reason)) {
            stats.blockedPromises++;
            console.log('🚫 Blocked extension promise rejection #' + stats.blockedPromises + ':', reason);
            e.preventDefault();
            e.stopPropagation();
            return false;
        }
    }, true);
    
    // 3. Override console methods
    const originalConsole = {
        error: console.error,
        warn: console.warn,
        log: console.log
    };
    
    console.error = function(...args) {
        const message = args.join(' ');
        if (isExtensionRelated(message)) {
            return; // Suppress extension errors
        }
        return originalConsole.error.apply(console, args);
    };
    
    console.warn = function(...args) {
        const message = args.join(' ');
        if (isExtensionRelated(message)) {
            return; // Suppress extension warnings
        }
        return originalConsole.warn.apply(console, args);
    };
    
    // 4. Block extension message listeners
    const originalAddEventListener = EventTarget.prototype.addEventListener;
    EventTarget.prototype.addEventListener = function(type, listener, options) {
        if (type === 'message' && listener) {
            const listenerStr = listener.toString();
            if (isExtensionRelated(listenerStr)) {
                console.log('🚫 Blocked extension message listener');
                return; // Block extension message listeners
            }
        }
        return originalAddEventListener.call(this, type, listener, options);
    };
    
    // 5. Block extension DOM manipulation
    function createDOMObserver() {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        // Check for extension-related attributes
                        const src = node.src || '';
                        const id = node.id || '';
                        const className = node.className || '';
                        const style = node.style ? node.style.cssText : '';
                        
                        if (isExtensionRelated(src) || 
                            isExtensionRelated(id) || 
                            isExtensionRelated(className) ||
                            (style.includes('z-index') && style.includes('214748'))) {
                            
                            console.log('🚫 Removed extension element:', node.tagName, id || className || src);
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
                attributes: true,
                attributeFilter: ['src', 'id', 'class', 'style']
            });
        } else {
            document.addEventListener('DOMContentLoaded', function() {
                observer.observe(document.body, { 
                    childList: true, 
                    subtree: true,
                    attributes: true,
                    attributeFilter: ['src', 'id', 'class', 'style']
                });
            });
        }
        
        return observer;
    }
    
    // 6. Block extension fetch/xhr requests
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {
        if (typeof url === 'string' && isExtensionRelated(url)) {
            console.log('🚫 Blocked extension fetch request:', url);
            return Promise.reject(new Error('Extension request blocked'));
        }
        return originalFetch.apply(this, arguments);
    };
    
    const originalXHROpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url) {
        if (typeof url === 'string' && isExtensionRelated(url)) {
            console.log('🚫 Blocked extension XHR request:', url);
            return;
        }
        return originalXHROpen.apply(this, arguments);
    };
    
    // 7. Block chrome.runtime access
    if (typeof chrome !== 'undefined' && chrome.runtime) {
        try {
            Object.defineProperty(chrome.runtime, 'sendMessage', {
                value: function() {
                    console.log('🚫 Blocked chrome.runtime.sendMessage');
                    return Promise.reject(new Error('Extension API blocked'));
                },
                writable: false
            });
        } catch (e) {
            // Ignore if can't override
        }
    }
    
    // 8. Initialize DOM observer
    const domObserver = createDOMObserver();
    
    // 9. Clean up existing extension elements
    function cleanupExtensionElements() {
        const selectors = [
            '[id*="extension"]',
            '[class*="extension"]',
            '[id*="chrome-extension"]',
            '[class*="chrome-extension"]',
            'iframe[src*="chrome-extension"]',
            'iframe[src*="moz-extension"]',
            '[data-extension]',
            '[id*="inlineForm"]',
            '[class*="inlineForm"]'
        ];
        
        selectors.forEach(selector => {
            try {
                const elements = document.querySelectorAll(selector);
                elements.forEach(el => {
                    console.log('🚫 Cleaned up extension element:', el.tagName, el.id || el.className);
                    el.remove();
                });
            } catch (e) {
                // Ignore selector errors
            }
        });
    }
    
    // 10. Run cleanup periodically
    setInterval(cleanupExtensionElements, 5000); // Every 5 seconds
    
    // 11. Run initial cleanup
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', cleanupExtensionElements);
    } else {
        cleanupExtensionElements();
    }
    
    console.log('✅ Extension Blocker: Comprehensive blocking initialized');
    
    // Export for debugging
    window.ExtensionBlocker = {
        isExtensionRelated,
        cleanupExtensionElements,
        observer: domObserver,
        stats: stats,
        getStats: function() {
            return {
                blockedErrors: stats.blockedErrors,
                blockedPromises: stats.blockedPromises,
                blockedRequests: stats.blockedRequests,
                removedElements: stats.removedElements,
                totalBlocked: stats.blockedErrors + stats.blockedPromises + stats.blockedRequests + stats.removedElements
            };
        }
    };
    
})();
