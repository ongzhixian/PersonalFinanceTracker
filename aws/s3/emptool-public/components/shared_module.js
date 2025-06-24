export const BASE_API_GATEWAY_ENDPOINT_URL = "https://7pps9elf11.execute-api.us-east-1.amazonaws.com";
export const AUTH_TICKET_STORAGE_KEY = "test_auth_ticket";

function AuthenticationModule() {

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
        return localStorage.getItem(AUTH_TICKET_STORAGE_KEY);
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