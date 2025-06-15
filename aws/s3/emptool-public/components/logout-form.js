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
<style>
#logoutForm {
    display: grid;
    grid-template-columns: 200px 1fr 1fr;
    grid-template-rows: repeat(3 1fr);
    grid-gap: .5rem;
}
#logoutForm label {
    justify-self: end;
    margin-right: .5rem;
}
</style>
<form id="logoutForm">
    
    <div></div>
    <input class="button-primary" type="button" value="logout" id="logoutButton" />
    <div></div>
    
</form>
`;
    }

}

customElements.define('logout-form', LogoutForm);
