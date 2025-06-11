// SHARED FUNCTIONS FOR ALL PAGES

////////////////////////////////////////
// FOR HANDLING LOGIN AND CREDENTIALS

function LoginHandler() {

    this.CREDENTIAL_STORAGE_KEY = "hci_blazer_view_credential";

    this.hasCredentialJwt = function() {
        let credentialJwt = localStorage.getItem(this.CREDENTIAL_STORAGE_KEY);
        return credentialJwt !== null;
    }

    this.storeCredential = function(credentialJwt) {
        return localStorage.setItem(this.CREDENTIAL_STORAGE_KEY, credentialJwt);
    }

    this.getCredentialJwt = function() {
        try {
            let credentialJwt = localStorage.getItem(this.CREDENTIAL_STORAGE_KEY);
            const base64Url = credentialJwt.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join(''));

            return JSON.parse(jsonPayload)
        } catch (e) {
            return null;
        }
    }

    this.getJwt = () => localStorage.getItem(this.CREDENTIAL_STORAGE_KEY);

    this.logout = function() {
        localStorage.removeItem(this.CREDENTIAL_STORAGE_KEY);
    }
}

function handleCredentialResponse(response) {
    console.log("Encoded JWT ID token: " + response.credential);
    //console.log("select_by: " + response.select_by);

    loginHandler.storeCredential(response.credential);

    uiHandler.refreshDisplay();
}

function sgpTimeString(locale = "en-SG") {
    const currentTime = (new Date);
    const localeIntl = new Intl.DateTimeFormat(locale);

    const localDate = localeIntl.format(currentTime);
    const timezoneName = localeIntl.resolvedOptions().timeZone;
    return `${localDate} ${currentTime.toLocaleTimeString()} (${timezoneName})`;
}

function AuthenticationTicketApiHandler() {
    this.AUTH_TICKET_STORAGE_KEY = "test_auth_ticket";
    this.storeAuthTicket = (authTicket) => localStorage.setItem(this.AUTH_TICKET_STORAGE_KEY, authTicket);
    this.getStoredAuthTicket = () => localStorage.getItem(this.AUTH_TICKET_STORAGE_KEY);
    this.hasAuthTicket = () => localStorage.getItem(this.AUTH_TICKET_STORAGE_KEY) !== null;
    this.logout = () => localStorage.removeItem(this.AUTH_TICKET_STORAGE_KEY);

    this.getAuthenticationTicket = async function(username, password) {

        let storedAuthTicket = this.getStoredAuthTicket();
        if (storedAuthTicket !== null)
            return storedAuthTicket;

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

        const responseJson = await response.json();
        if (responseJson.is_success && responseJson.data_object) {
            this.storeAuthTicket(responseJson.data_object.token);
            return responseJson.data_object.token;
        } else {
            console.warn('Validation failed: ', responseJson.message);
            return null;
        }
    }
}