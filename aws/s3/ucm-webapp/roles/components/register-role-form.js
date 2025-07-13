import RoleModule from './role-module.js';

class RegisterRoleForm extends HTMLElement {

    #roleModule;
    #elements = {}; // Centralized storage for DOM elements
    #boundListeners = {}; // Centralized storage for bound event listeners

    constructor() {
        super();
        this.#roleModule = new RoleModule();
        this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
        this.#render();
        this.#cacheDomElements();
        this.#addEventListeners();
        this.#initializeFormState(); // Ensure initial state is correct
    }

    disconnectedCallback() {
        this.#removeEventListeners();
    }

    /**
     * Renders the component's HTML content from a template.
     * @private
     */
    #render() {
        const template = document.getElementById("registerRoleFormTemplate");
        if (!template) {
            console.error("Template 'registerRoleFormTemplate' not found.");
            return;
        }
        this.shadowRoot.appendChild(template.content.cloneNode(true));
    }

    /**
     * Adds event listeners to the relevant DOM elements.
     * Uses bound methods stored in #boundListeners to ensure correct 'this' context.
     * @private
     */
    #addEventListeners() {
        this.#boundListeners.onRegisterButtonClicked = this.#onRegisterButtonClicked.bind(this);
        this.#elements.registerButton?.addEventListener('click', this.#boundListeners.onRegisterButtonClicked);
    }

    /**
     * Removes event listeners to prevent memory leaks.
     * @private
     */
    #removeEventListeners() {
        this.#elements.registerButton?.removeEventListener('click', this.#boundListeners.onRegisterButtonClicked);
    }

    /**
     * Sets the initial display state of the form and feedback sections.
     * @private
     */
    #initializeFormState() {
        this.#elements.registerRoleForm?.classList.remove('hide');
        this.#elements.sectionFeedback?.classList.add('hide');
        this.#elements.errorMessage?.classList.add('hide');
    }

    /**
     * Caches references to frequently used DOM elements.
     * @private
     */
    #cacheDomElements() {
        const selectors = {
            registerRoleForm: 'form#registerRoleForm',
            errorMessage: 'div#errorMessage',
            nameInput: '#nameInput',
            descriptionInput: '#descriptionInput',
            statusOption: '#statusOption',
            registerButton: '#registerButton',
        };

        this.#elements = Object.fromEntries(
            Object.entries(selectors).map(([key, selector]) => [
                key,
                this.shadowRoot.querySelector(selector)
            ])
        );
    }


    /**
     * Handles the click event for the register button.
     * @param {Event} e - The click event object.
     * @private
     */
    async #onRegisterButtonClicked(e) {
        e.preventDefault(); // Prevent default form submission behavior
        console.debug("Register button clicked.");

        const { nameInput, descriptionInput, statusOption, errorMessage, registerRoleForm, registerButton } = this.#elements;

        registerButton.disabled = true;
        //registerButton.attribute('disabled', 'true'); // Disable button to prevent multiple clicks
        

        if (!nameInput.value || !statusOption.value) {
            this.#updateErrorMessage("All fields are required.");
            return;
        }

        this.#hideErrorMessage(); // Clear previous error messages

        try {
            console.debug("Simulating registration process...");
            const registrationDetail = {
                name: nameInput.value,
                description: descriptionInput.value,
                status: statusOption.value
            }
            console.dir(registrationDetail);
            
            const registrationResponse = await this.#roleModule.registerRole(registrationDetail);
            if (registrationResponse.is_success) {
                console.log("Registration successful:", registrationResponse.message);
                this.#showSuccessFeedback(registrationResponse.message);
            } else {
                this.#updateErrorMessage(registrationResponse.message || "Registration failed. Please try again.");
            }

        } catch (error) {
            console.error("Error during registration:", error);
            this.#updateErrorMessage("An unexpected error occurred during registration.");
        }

        registerButton.disabled = false;
    }

    /**
     * Handles the click event for the "Register Another" button.
     * @param {Event} e - The click event object.
     * @private
     */
    #onRegisterAnotherButtonClicked(e) {
        console.debug("Register another button clicked.");

        // Clear the form inputs
        this.#elements.usernameInput.value = '';
        this.#elements.passwordInput.value = '';
        this.#elements.passwordConfirmInput.value = '';

        // Reset form display
        this.#elements.errorMessage?.classList.add('hide');
        this.#elements.sectionFeedback?.classList.add('hide');
        this.#elements.loginForm?.classList.remove('hide');
    }


    /**
     * Displays an error message to the user.
     * @param {string} message - The error message to display.
     * @private
     */
    #updateErrorMessage(message) {
        if (this.#elements.errorMessage) {
            this.#elements.errorMessage.innerHTML = `<span>${message}</span>`;
            this.#elements.errorMessage.classList.remove('hide');
        }
    }

    /**
     * Hides the error message.
     * @private
     */
    #hideErrorMessage() {
        this.#elements.errorMessage?.classList.add('hide');
        this.#elements.errorMessage.innerHTML = ''; // Clear content when hidden
    }

    /**
     * Shows success feedback to the user and hides the form.
     * @param {string} message - The success message to display.
     * @private
     */
    #showSuccessFeedback(message) {
        if (this.#elements.sectionFeedback && this.#elements.loginForm) {
            // Assuming there's a paragraph element to update message
            const feedbackParagraph = this.#elements.sectionFeedback.querySelector('p');
            if (feedbackParagraph) {
                feedbackParagraph.innerHTML = message;
            }
            this.#elements.loginForm.classList.add('hide');
            this.#elements.sectionFeedback.classList.remove('hide');
            this.#hideErrorMessage(); // Ensure error message is hidden on success
        }
    }
}

customElements.define('register-role-form', RegisterRoleForm);
