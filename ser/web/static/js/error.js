// Error handling and asset loading management

class ErrorHandler {
    constructor() {
        this.setupErrorListeners();
        this.setupUIHandlers();
    }

    setupErrorListeners() {
        // Handle resource loading errors
        window.addEventListener('error', (event) => {
            if (event.target instanceof HTMLImageElement || 
                event.target instanceof HTMLScriptElement || 
                event.target instanceof HTMLLinkElement) {
                this.handleResourceError(event);
            }
        }, true);

        // Handle general JavaScript errors
        window.onerror = (msg, url, lineNo, columnNo, error) => {
            this.logError({
                type: 'javascript',
                message: msg,
                url: url,
                line: lineNo,
                column: columnNo,
                error: error?.stack
            });
            return false;
        };

        // Handle unhandled promise rejections
        window.onunhandledrejection = (event) => {
            this.logError({
                type: 'promise',
                message: event.reason?.message || 'Unhandled Promise Rejection',
                error: event.reason?.stack
            });
        };
    }

    setupUIHandlers() {
        document.addEventListener('DOMContentLoaded', () => {
            // Set up "Go Back" button
            const goBackBtn = document.querySelector('button.secondary');
            if (goBackBtn) {
                goBackBtn.addEventListener('click', () => history.back());
            }

            // Set up "Go to Dashboard" button
            const dashboardBtn = document.querySelector('a.primary');
            if (dashboardBtn) {
                dashboardBtn.addEventListener('click', (e) => {
                    // Verify dashboard page availability before navigation
                    this.verifyResourceAvailability('/');
                });
            }
        });
    }

    handleResourceError(event) {
        const target = event.target;
        const resourceType = target.tagName.toLowerCase();
        const resourceUrl = target.src || target.href;

        this.logError({
            type: 'resource',
            resourceType: resourceType,
            url: resourceUrl,
            message: `Failed to load ${resourceType} resource`
        });

        // Handle 404 errors specifically
        if (event.target.status === 404) {
            this.handle404Error(resourceUrl);
        }
    }

    handle404Error(resourceUrl) {
        console.error(`Resource not found: ${resourceUrl}`);
        // Redirect to 404 page for critical resources
        if (this.isCriticalResource(resourceUrl)) {
            window.location.href = '/404';
        }
    }

    isCriticalResource(url) {
        const criticalPaths = [
            '/static/css/style.css',
            '/static/js/dashboard.js'
        ];
        return criticalPaths.some(path => url.includes(path));
    }

    verifyResourceAvailability(url) {
        fetch(url, { method: 'HEAD' })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
            })
            .catch(error => {
                this.logError({
                    type: 'navigation',
                    url: url,
                    message: error.message
                });
                window.location.href = '/404';
            });
    }

    logError(errorData) {
        // Log to console for development
        console.error('Error occurred:', errorData);

        // Send error to server for logging
        fetch('/api/log-error', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(errorData)
        }).catch(err => {
            console.error('Failed to log error:', err);
        });
    }
}

// Initialize error handler
const errorHandler = new ErrorHandler();

console.log("Error handling system initialized with asset loading management.");

console.log("Archivo error.js creado con lógica básica para las páginas de error.");