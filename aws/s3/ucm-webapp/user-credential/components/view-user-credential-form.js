import UserCredentialModule from './user-credential-module.js';

class ViewUserCredentialForm extends HTMLElement {

    static get observedAttributes() {
        return ['username'];
    }

    apiCallFailed = (failureReason) => {
        console.log('Fail to get record:', failureReason);
    }

    apiCallSucceed = (data) => {
        console.log(data);
    }

    apiCallDone = () => {
        console.log("API call done");
    }

    async attributeChangedCallback(name, oldValue, newValue) {
        console.log('attributeChangedCallback');
        if (name === 'username' && oldValue !== newValue) {
            this._updateUsername(newValue);
            const responseContent = await this.userCredentialModule.getUserCredential(newValue);
            // .then(this.apiCallSucceed, this.apiCallFailed)
            // .catch(this.apiCallFailed)
            // .finally(this.apiCallDone);
            console.debug('ResponseContent:', responseContent)

            const data = responseContent.data_object;
            this._lastLoginDisplay.textContent = data['last_successful_login'] ?? 'N/A';
            this._failedAttemptsDisplay.textContent = data['failed_login_attempts'] ?? 'N/A';
            this._lastFailedAttemptDisplay.textContent = data['last_login_attempt_datetime'] ?? 'N/A';
            this._statusSelect.value = data['status'];

        }
    }

    render() {
        const template = document.getElementById('viewUserCredentialTemplate');
        if (!template) {
            const templateNotFoundErrorMessage = "Template with ID 'viewUserCredentialTemplate' not found.";
            console.error(templateNotFoundErrorMessage);
            this.shadowRoot.innerHTML = `<p>Error: ${templateNotFoundErrorMessage}</p>`;
            return;
        }

        this.shadowRoot.appendChild(template.content.cloneNode(true));
        console.log('Render')
    }

    #setupDomReferences() {
        this._usernameDisplay = this.shadowRoot.getElementById('usernameDisplay');
        this._lastLoginDisplay = this.shadowRoot.getElementById('lastLoginDisplay');
        this._failedAttemptsDisplay = this.shadowRoot.getElementById('failedAttemptsDisplay');
        this._lastFailedAttemptDisplay = this.shadowRoot.getElementById('lastFailedAttemptDisplay');
        this._statusSelect = this.shadowRoot.getElementById('statusSelect');
        this.updateButton = this.shadowRoot.getElementById('updateButton');
    }

    #updateEventHandler = (event) => {
        console.log('TODO: Update: ', this.getAttribute('username'), 'to ...?', this._statusSelect.value);
    }
    /**
     * Adds event listeners to the relevant DOM elements.
     * Uses bound methods stored in #boundListeners to ensure correct 'this' context.
     * @private
     */
    #addEventListeners() {
        this.updateButton?.addEventListener('click', this.#updateEventHandler);
    }

    /**
     * Removes event listeners to prevent memory leaks.
     * @private
     */
    #removeEventListeners() {
        this.updateButton?.removeEventListener('click', this.#updateEventHandler);
    }

    _updateUsername(username) {
        const displayValue = username || 'N/A';
        if (this._usernameDisplay) {
            this._usernameDisplay.textContent = displayValue;
        }
        // if (this._usernameStrong) {
        //     this._usernameStrong.textContent = displayValue;
        // }
    }


    // STANDARD SETUP

    constructor() {
        super();
        this.userCredentialModule = new UserCredentialModule();
        this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
        this.render();
        this.#setupDomReferences();
        this.#addEventListeners()
        // this.#initializeFormState(); // Ensure initial state is correct
    }

    disconnectedCallback() {
        this.#removeEventListeners();
        // Good practice to nullify the reference to aid garbage collection
        //eg: this.myButton = null;
    }

}

customElements.define('view-user-credential-form', ViewUserCredentialForm);
