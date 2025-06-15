class LoginForm extends HTMLElement {
    AUTH_TICKET_STORAGE_KEY = "test_auth_ticket";

    constructor() {
        super(); // Always call super first in constructor
        this.onLoginButtonClicked = (e) => this.#onLoginButtonClicked(e);
        this.authenticator = new AuthenticationModule();
        this.attachShadow({ mode: 'open' });
    }
    
    connectedCallback() {
        this.render();
        this.usernameInput = this.shadowRoot.querySelector('#usernameInput');
        this.passwordInput = this.shadowRoot.querySelector('#passwordInput');
        this.loginButton = this.shadowRoot.querySelector('#loginButton');
        this.loginButton.addEventListener('click', this.onLoginButtonClicked);
    }

    disconnectedCallback() {
        this.loginButton.removeEventListener('click', this.loginButtonClicked);
    }

    async #onLoginButtonClicked(e) {
        console.log("Login button clicked.");

        let isValidCredential = await this.authenticator.validateCredentials(this.usernameInput.value, this.passwordInput.value);

        if (isValidCredential) {
            window.location.href = '/index.html'; // Redirect to home page
            return;
        }
        
        console.error("Validation failed. Please check your credentials.");
        

        //this.AUTH_TICKET_STORAGE_KEY = "test_auth_ticket";
        //this.storeAuthTicket = (authTicket) => localStorage.setItem(this.AUTH_TICKET_STORAGE_KEY, authTicket);
        //this.getStoredAuthTicket = () => localStorage.getItem(this.AUTH_TICKET_STORAGE_KEY);
        //this.hasAuthTicket = () => localStorage.getItem(this.AUTH_TICKET_STORAGE_KEY) !== null;
        //this.logout = () => localStorage.removeItem(this.AUTH_TICKET_STORAGE_KEY);

        //this.getAuthenticationTicket = async function (username, password) {

        //    let storedAuthTicket = this.getStoredAuthTicket();
        //    if (storedAuthTicket !== null)
        //        return storedAuthTicket;

        //    const endpoint_url = 'https://7pps9elf11.execute-api.us-east-1.amazonaws.com/authentication-ticket';
        //    const requestHeaders = new Headers();
        //    requestHeaders.append("Content-Type", "application/json");

        //    const response = await fetch(endpoint_url, {
        //        method: "POST",
        //        headers: requestHeaders,
        //        body: JSON.stringify({
        //            username: username,
        //            password: password
        //        })
        //    });
        //}

    }

    render() {
        this.shadowRoot.innerHTML = `
<style>
#loginForm {
    display: grid;
    grid-template-columns: 200px 1fr 1fr;
    grid-template-rows: repeat(3 1fr);
    grid-gap: .5rem;
}
#loginForm label {
    justify-self: end;
    margin-right: .5rem;
}
</style>
<form id="loginForm">
    <label for="usernameInput">Username</label>
    <input class="u-full-width" type="text" placeholder="Username (email)" id="usernameInput" value="testuser1" />
    <div></div>

    <label for="passwordInput">Password</label>
    <input class="u-full-width" type="password" placeholder="Password" id="passwordInput" value="testuser1a" />
    <div></div>

    <div></div>
    <input class="button-primary" type="button" value="login" id="loginButton" />
    <div></div>
    
</form>
`;
    }

}

customElements.define('login-form', LoginForm);
