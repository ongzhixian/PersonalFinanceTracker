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