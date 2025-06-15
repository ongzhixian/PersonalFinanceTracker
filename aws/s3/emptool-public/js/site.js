// SHARED FUNCTIONS FOR ALL PAGES

////////////////////////////////////////
// FOR HANDLING LOGIN AND CREDENTIALS

function LoginHandler() {

    this.CREDENTIAL_STORAGE_KEY = "ucm_credential";

    this.hasCredentialJwt = function () {
        let credentialJwt = localStorage.getItem(this.CREDENTIAL_STORAGE_KEY);
        return credentialJwt !== null;
    }

    this.storeCredential = function (credentialJwt) {
        return localStorage.setItem(this.CREDENTIAL_STORAGE_KEY, credentialJwt);
    }

    this.getCredentialJwt = function () {
        try {
            let credentialJwt = localStorage.getItem(this.CREDENTIAL_STORAGE_KEY);
            const base64Url = credentialJwt.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function (c) {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join(''));

            return JSON.parse(jsonPayload)
        } catch (e) {
            return null;
        }
    }

    this.getJwt = () => localStorage.getItem(this.CREDENTIAL_STORAGE_KEY);

    this.logout = function () {
        localStorage.removeItem(this.CREDENTIAL_STORAGE_KEY);
    }
}

function AuthenticationModule() {
    this.AUTH_TICKET_STORAGE_KEY = "test_auth_ticket";

    this.validateCredentials = async (username, password) => {
        console.log("Validating credentials for", username, password);
        const endpoint_url = 'https://7pps9elf11.execute-api.us-east-1.amazonaws.com/authentication-ticket';
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
            localStorage.setItem(this.AUTH_TICKET_STORAGE_KEY, validationResult.data_object['token']);
            return true;
        }

        return false;
    }

    this.isAuthenticated = () => {
        return localStorage.getItem(this.AUTH_TICKET_STORAGE_KEY) !== null;
    }

    this.logout = () => {
        localStorage.removeItem(this.AUTH_TICKET_STORAGE_KEY);
    }
}

function ChannelHandler(initiator) {
    //console.log(initiator, 'ChannelHandler');
    this.broadcastChannel = new BroadcastChannel("test_channel");

    this.sendMessage = function (messageContent) {
        this.broadcastChannel.postMessage(messageContent);
    }

    this.subscribe = function (eventHandler) {
        //this.broadcastChannel.onmessage = (event) => eventHandler(event);
        this.broadcastChannel.onmessage = eventHandler;
    }

    this.leaveChannel = function () {
        this.broadcastChannel.close();
    }
}

document.addEventListener("DOMContentLoaded", () => {
    if (this.window.location.pathname === "/login.html") return;

    window.authenticator = new AuthenticationModule();
    if (!window.authenticator.isAuthenticated())
        window.location.href = '/login.html'; // Redirect to login page if not authenticated
});