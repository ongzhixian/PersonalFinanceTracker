class LogoutForm extends HTMLElement {

    constructor() {
        super(); // Always call super first in constructor
        this.logoutButtonClickedHandler = (e) => this.#logoutButtonClickedHandler(e);
        this.attachShadow({ mode: 'open' });
    }
    
    connectedCallback() {
        this.render();
        this.logoutButton = this.shadowRoot.querySelector('#logoutButton');
        this.logoutButton.addEventListener('click', this.logoutButtonClickedHandler);
    }

    disconnectedCallback() {
        this.logoutButton.removeEventListener('click', this.loginButtonClicked);
    }

    async #logoutButtonClickedHandler(e) {
        await window.authenticator.logout();
        window.location.href = '/login.html'; // Redirect to home page
    }

    render() {
        this.shadowRoot.innerHTML = `
<form id="logoutForm">
    
    <p>Are you sure you want to logout?</p>

    <input class="button-primary" type="button" value="Confirm log out" id="logoutButton" />
    
</form>
`;
    }

}

customElements.define('logout-form', LogoutForm);
