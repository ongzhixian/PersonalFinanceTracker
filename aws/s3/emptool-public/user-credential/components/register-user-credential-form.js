import UserCredentialModule from './user-credential-module.js';

class RegisterUserCredentialForm extends HTMLElement {

    constructor() {
        super();
        this.onRegisterButtonClicked = (e) => this.#onRegisterButtonClicked(e);
        this.onRegisterAnotherButtonClicked = (e) => this.#onRegisterAnotherButtonClicked(e);
        this.userCredentialModule = new UserCredentialModule();
        this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
        this.render();
        this.sectionFeedback = this.shadowRoot.querySelector('section.feedback');
        this.loginForm = this.shadowRoot.querySelector('form#loginForm');

        this.errorMessage = this.shadowRoot.querySelector('div#errorMessage');
        this.usernameInput = this.shadowRoot.querySelector('#usernameInput');
        this.passwordInput = this.shadowRoot.querySelector('#passwordInput');
        this.passwordConfirmInput = this.shadowRoot.querySelector('#passwordConfirmInput');
        this.registerButton = this.shadowRoot.querySelector('#registerButton');
        this.registerButton.addEventListener('click', this.onRegisterButtonClicked);

        this.registerAnotherButton = this.shadowRoot.querySelector('#registerAnotherButton');
        this.registerAnotherButton.addEventListener('click', this.onRegisterAnotherButtonClicked);
    }

    disconnectedCallback() {
        this.registerButton.removeEventListener('click', this.onRegisterButtonClicked);
    }

    async #onRegisterButtonClicked(e) {
        console.debug("Register button clicked.");

        // Validate the form inputs
        if (this.usernameInput.value === '' || this.passwordInput.value === '' || this.passwordConfirmInput.value === '') {

        }

        let registrationResponse = await this.userCredentialModule.registerUserCredential(this.usernameInput.value, this.passwordInput.value);
        console.log('registrationResponse', registrationResponse);

        // {is_success: true, message: 'testuser5 added successfully', data_object: null}
        if (registrationResponse.is_success) {
            console.log("Registration successful:", registrationResponse.message);
            // Hide form and show feedback
            //this.sectionFeedback.getElementsByTagName('p')[0].innerHTML = registrationResponse.message;
            this.loginForm.classList.add('hide');
            this.sectionFeedback.classList.remove('hide');
        } else {
            // Update the error messaage and show feedback
            this.errorMessage.innerHTML = `<span>${registrationResponse.message}</span>`;
            this.errorMessage.classList.remove('hide');
        }
    }

    async #onRegisterAnotherButtonClicked(e) {
        console.debug("Register another button clicked.");

        // Clear the form inputs
        this.usernameInput.value = '';
        this.passwordInput.value = '';
        this.passwordConfirmInput.value = '';

        // Hide feedback section and show the form again
        this.errorMessage.classList.add('hide');
        this.sectionFeedback.classList.add('hide');
        this.loginForm.classList.remove('hide');
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
.error {
    color: var(--color8);
}
.tooltips span {
    cursor: help;
}
.tooltips span:hover {
    color: var(--color9);
}
</style>
<section class="feedback hide">
    <p>Added successfully</p>

    <div>
        <input class="button-primary" type="button" value="Register another" id="registerAnotherButton" />
    </div>
</section>
<form id="loginForm">
    <label for="usernameInput">Username</label>
    <input class="u-full-width" type="text" placeholder="Username (email)" id="usernameInput" value="testuser5" />
    <div class='tooltips'><span title='Required'>&sharp;1</span> <span title='Existing'>&sharp;2</span></div>

    <label for="passwordInput">Password</label>
    <input class="u-full-width" type="password" placeholder="Password" id="passwordInput" value="testuser5a" />
    <div class='tooltips'><span title='Mismatching'>&sharp;3</span></div>

    <label for="passwordConfirmInput">Password<br/>(confirm)</label>
    <input class="u-full-width" type="password" placeholder="Password" id="passwordConfirmInput" value="testuser5a" />
    <div class='tooltips'><span title='Mismatching'>&sharp;3</span></div>

    <div></div>
    <div>
        <input class="button-primary" type="button" value="Register" id="registerButton" />
        <div class="error message hide" id="errorMessage"><div>
    </div>
    <div></div>
</form>
`;
    }

}

customElements.define('register-user-credential-form', RegisterUserCredentialForm);
