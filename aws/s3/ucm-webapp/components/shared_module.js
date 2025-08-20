export const BASE_API_GATEWAY_ENDPOINT_URL = "https://7pps9elf11.execute-api.us-east-1.amazonaws.com";
export const AUTH_TICKET_STORAGE_KEY = "test_auth_ticket";

export function AuthenticationModule() {

    this.validateCredentials = async (username, password) => {
        console.log("Validating credentials for", username, password);
        const endpoint_url = `${BASE_API_GATEWAY_ENDPOINT_URL}/authentication-ticket`;
        const requestHeaders = new Headers();
        requestHeaders.append("Content-Type", "application/json");

        const response = await fetch(endpoint_url, {
            method: "POST",
            headers: requestHeaders,
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        if (!response.ok) throw new Error("Authentication failed: " + response.statusText);

        const validationResult = await response.json();
        if (validationResult.data_object && 'token' in validationResult.data_object) {
            localStorage.setItem(AUTH_TICKET_STORAGE_KEY, validationResult.data_object['token']);
            return true;
        }

        return false;
    }

    this.isAuthenticated = () => {
        return localStorage.getItem(AUTH_TICKET_STORAGE_KEY) !== null;
    }

    this.getToken = () => {
        const token = localStorage.getItem(AUTH_TICKET_STORAGE_KEY);

        if (token !== null) return token;

        throw new Http401Unauthorized("Unauthorized: No authentication token found.");
    }

    this.logout = () => {
        localStorage.removeItem(AUTH_TICKET_STORAGE_KEY);
    }

    this.urlsafeBase64Decode = function (str) {

        // Replace URL-safe characters with standard Base64 characters
        str = str.replace(/-/g, '+').replace(/_/g, '/');
        // Pad with '=' to make the length a multiple of 4
        while (str.length % 4) {
            str += '=';
        }
        // Decode
        return atob(str);
    }

    this.getParsedToken = function () {
        const token = localStorage.getItem(AUTH_TICKET_STORAGE_KEY);
        if (!token) return null;

        const tokenParts = this.urlsafeBase64Decode(token).slice(0, -32).split('|');

        if (tokenParts.length < 2) return null;

        return {
            expiry: tokenParts[0],
            username: tokenParts[1]
        };
    }
}

export function UiModule() {

    this.get_template_or_throw = (templateElementId) => {
        const templateHtmlElement = document.getElementById(templateElementId);
        if (templateHtmlElement) return templateHtmlElement;

        const errorMessage = `Template '${templateElementId}' not found. Please ensure it is defined in the HTML.`;
        // console.error(errorMessage); // redundant since throw error
        throw new Error(errorMessage);
    }

    // this.showErrorMessage = (message) => {
    //     const errorMessageElement = document.querySelector('.error-message');
    //     if (errorMessageElement) {
    //         errorMessageElement.textContent = message;
    //         errorMessageElement.style.display = 'block';
    //     }
    // }
    //
    // this.hideErrorMessage = () => {
    //     const errorMessageElement = document.querySelector('.error-message');
    //     if (errorMessageElement) {
    //         errorMessageElement.style.display = 'none';
    //     }
    // }
    //
    // this.showSuccessFeedback = (message) => {
    //     const successFeedbackElement = document.querySelector('.success-feedback');
    //     if (successFeedbackElement) {
    //         successFeedbackElement.textContent = message;
    //         successFeedbackElement.style.display = 'block';
    //     }
    // }
}

export function HttpModule(authenticationModule = new AuthenticationModule()) {

    this.authenticationModule = authenticationModule;

    this.getRequestHeaders = () => {
        const jwt = this.authenticationModule.getToken();
        return {
            "Content-Type": "application/json",
            "Authorization": `TOKEN ${jwt}`
        }
    }

}

/**
 * Returns a standardized error response object.
 * @param {Response} response - The original fetch response object.
 * @returns {{is_success: boolean, message: string, data_object: null}}
 */
export function notOkResponse(response) {
    // TODO: Add more detailed error handling based on response status codes
    return {
        is_success: false,
        message: response.statusText,
        data_object: null
    }
}


/**
 * Custom error class representing an HTTP 401 Unauthorized error.
 * Use this to signal authentication failures or unauthorized access attempts.
 *
 * @extends Error
 * @param {string} message - Error message describing the unauthorized access.
 * @property {string} statusText - HTTP status text ("Unauthorized").
 * @property {number} status - HTTP status code (401).
 */
export class Http401Unauthorized extends Error {
    constructor(message) {
        super(message);
        this.statusText = "Unauthorized";
        this.status = 401;
    }
}
