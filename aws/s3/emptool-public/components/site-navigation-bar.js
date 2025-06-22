class NavItem extends HTMLElement {

    static observedAttributes = ["componentName", "active"];

    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
        this.render();
        this.shadowRoot.querySelector('.nav-item').addEventListener('click', () => {
            console.log(`NavItem clicked: ${this.getAttribute('componentName')}`);
            const isActive = this.getAttribute('active') === 'true';
            this.setAttribute('active', isActive ? 'false' : 'true');
        });
    }

    attributeChangedCallback(name, oldValue, newValue) {
        console.log(`NavItem Attribute ${name} changed from ${oldValue} to ${newValue}`);
    }

    render() {
        this.shadowRoot.innerHTML = `
<style>
span.nav-item {
    cursor: pointer;
}
span.nav-item:hover {
        color: #ffffff;
    }
span.nav-item.active {
    color: #fff275;
    font-weight: bold;
}
</style>
<span class='nav-item ${this.getAttribute("active") === "true" ? "active" : ""}'>${this.textContent}</span>`;

    }
}


class SiteNavigationBar extends HTMLElement {
    //static observedAttributes = ["color", "size"];

    constructor() {
        super(); // Always call super first in constructor
        this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
        //console.log("SiteNavigationBar added to page.");
        this.render();
    }

    disconnectedCallback() {
        //console.log("SiteNavigationBar removed from page.");
    }

    connectedMoveCallback() {
        //console.log("SiteNavigationBar moved with moveBefore()");
    }

    adoptedCallback() {
        //console.log("SiteNavigationBar moved to new page.");
    }

    attributeChangedCallback(name, oldValue, newValue) {
        //console.log(`Attribute ${name} has changed.`);
    }

    render() {
        this.shadowRoot.innerHTML = `
<style>
    :host {}
    h1 {
        font-size: 4.0rem;
        font-weight: 300;
    }
    nav {
        background-color: #1282a2;
        display: flex;
        justify-items: center;
        justify-content: center;
        gap: 1em;
        padding:1em;
        margin-bottom:1em;
    }
    nav a {
        padding: 0.8rem 1.6rem;
        border-radius: 1em;
        text-decoration: none;
        color: #fefcfb;
    }
    nav a:hover {
        color: #fff275;
    }
</style>
<nav>
    <div><a href="/">Home</a></div>
    <div><a href="/user-credential/index.html">User Credentials</a></div>
    <div><a href="/memberships.html">Memberships</a></div>
    <div><a href="/configurations.html">Configurations</a></div>
</nav>`;
    }
}


// Define the custom elements

customElements.define('nav-item', NavItem);
customElements.define('site-navigation-bar', SiteNavigationBar);
