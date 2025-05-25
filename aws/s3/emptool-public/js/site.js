// SHARED FUNCTIONS FOR ALL PAGES

////////////////////////////////////////
// FOR HANDLING LOGIN AND CREDENTIALS

function LoginHandler() {

    this.CREDENTIAL_STORAGE_KEY = "ucm_credential";

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