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
  <div><a href="/user-credentials.html">User Credentials</a></div>
  <div><a href="/memberships.html">Memberships</a></div>
</nav>`;
    }

}

customElements.define('site-navigation-bar', SiteNavigationBar);
