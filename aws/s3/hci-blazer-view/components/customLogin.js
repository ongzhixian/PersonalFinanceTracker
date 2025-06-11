class CustomLogin extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    static get observedAttributes() {
        return ['name'];
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (name === 'name') {
            this.render();
        }
    }

    connectedCallback() {
        this.render();
    }

    render() {
        const currentPage = window.location.pathname;
        this.shadowRoot.innerHTML = `
<style>
:host {
    font-family: inherit;
}

.button, button, input[type="submit"], input[type="reset"], input[type="button"] {
    display: inline-block;
    height: 38px;
    padding: 0 30px;
    color: #555;
    text-align: center;
    font-size: 11px;
    font-weight: 600;
    line-height: 38px;
    letter-spacing: .1rem;
    text-transform: uppercase;
    text-decoration: none;
    white-space: nowrap;
    background-color: transparent;
    border-radius: 4px;
    border: 1px solid #bbb;
    cursor: pointer;
    box-sizing: border-box;
}

input[type=button] {
    color: #FFF;
    background-color: #33C3F0;
    border-color: #33C3F0;
    font-family: inherit;
}
</style>
<section id="customLoginPanel" class="panel hide" style="margin-top:1em;">

    <form id="customLoginForm">
        <div class="row">
            <div class="six columns">
                <label for="usernameInput">Username</label>
                <input class="u-full-width" type="text" placeholder="Email" id="usernameInput" value="testuser1" />
            </div>
        </div>
        <div class="row">
            <div class="six columns">
                <label for="passwordInput">Password</label>
                <input class="u-full-width" type="password" placeholder="Password" id="passwordInput" value="testuser1a" />
            </div>
        </div>

        <input class="button-primary" type="button" value="Validate Credential" id="validateCredentialButton" />
    </form>

</section>
    `;
    }
}

customElements.define('custom-login', CustomLogin);