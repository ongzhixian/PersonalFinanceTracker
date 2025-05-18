class MyGreeting extends HTMLElement {
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
        const name = this.getAttribute('name') || 'Guest';
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: inline-block;
                    padding: 10px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    background-color: #f9f9f9;
                }
                .greeting {
                    font-weight: bold;
                    color: blue;
                }
            </style>
            <div class="greeting">Hello, ${name}!</div>
        `;
    }
}

customElements.define('my-greeting', MyGreeting);