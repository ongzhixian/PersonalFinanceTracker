class RegisterUserCredentialForm extends HTMLElement {
    AUTH_TICKET_STORAGE_KEY = "test_auth_ticket";

    constructor() {
        super(); // Always call super first in constructor
        this.onRegisterButtonClicked = (e) => this.#onRegisterButtonClicked(e);
        this.authenticator = new AuthenticationModule();
        this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
        this.render();
        this.usernameInput = this.shadowRoot.querySelector('#usernameInput');
        this.passwordInput = this.shadowRoot.querySelector('#passwordInput');
        this.registerButton = this.shadowRoot.querySelector('#registerButton');
        this.registerButton.addEventListener('click', this.onRegisterButtonClicked);
    }

    disconnectedCallback() {
        this.registerButton.removeEventListener('click', this.onRegisterButtonClicked);
    }

    async #onRegisterButtonClicked(e) {
        console.debug("Register button clicked.");

        // let isValidCredential = await this.authenticator.validateCredentials(this.usernameInput.value, this.passwordInput.value);

        // if (isValidCredential) {

        //     const params = new URLSearchParams(window.location.search);
        //     if (params.has('redirect')) {
        //         window.location.href = params.get('redirect')
        //     } else {
        //         window.location.href = '/index.html'; // Redirect to home page
        //     }
        //     return;
        // }

        //console.error("Validation failed. Please check your credentials.");

    }

    render() {
        this.shadowRoot.innerHTML = `
<link rel="stylesheet" href="/css/normalize.css" />
<link rel="stylesheet" href="/css/skeleton.css" />
<link rel="stylesheet" href="/css/site.css" />
<style>
#loginForm {
    display: grid;
    grid-template-columns: 5rem 18rem 5rem;
    grid-template-rows: repeat(3, 1fr);
    grid-gap: .5rem;
    justify-content: center;
    margin-top: 4rem;
    align-items: center;
}
#loginForm label {
    justify-self: end;
    margin-right: .5rem;
    margin-bottom: 1.5rem;
}
</style>
<form id="loginForm">
    <label for="usernameInput">Username</label>
    <input class="u-full-width" type="text" placeholder="Username (email)" id="usernameInput" value="testuser1" />
    <div></div>

    <label for="passwordInput">Password</label>
    <input class="u-full-width" type="password" placeholder="Password" id="passwordInput" value="testuser1a" />
    <div></div>

    <label for="passwordInput">Password<br/>(confirm)</label>
    <input class="u-full-width" type="password" placeholder="Password" id="passwordInput" value="testuser1a" />
    <div></div>

    <div></div>
    <input class="button-primary" type="button" value="Register" id="registerButton" />
    <div></div>
    
</form>
`;
    }

}

customElements.define('register-user-credential-form', RegisterUserCredentialForm);
