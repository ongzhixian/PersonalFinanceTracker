class NavItem extends HTMLElement {

    static observedAttributes = ["name", "content-path", "active"];

    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.handleNavClick = () => this.navItemOnClick();
    }

    connectedCallback() {
        this.render();
        //this.shadowRoot.querySelector('.nav-item').addEventListener('click', () => {
        //    console.log(`NavItem clicked: ${this.getAttribute('componentName')}`);
        //    const isActive = this.getAttribute('active') === 'true';
        //    this.setAttribute('active', isActive ? 'false' : 'true');

        //    let event = new CustomEvent('my-custom-event', {
        //        composed: true,
        //        bubbles: true,
        //        cancelable: true,
        //        detail: 'This is awesome. I could also be an object or array.'
        //    });
        //    // Emit the event
        //    this.dispatchEvent(event);
        //});

        this.navItem = this.shadowRoot.querySelector('.nav-item');
        this.navItem.addEventListener('click', this.handleNavClick);
        //this.navItem.addEventListener('click', this.navItemOnClick.bind(this));
    }

    navItemOnClick() {
        
        const isActive = this.getAttribute('active') === 'true';
        this.setAttribute('active', isActive ? 'false' : 'true');

        //console.log(`NavItem clicked: ${this.getAttribute('name')}, ${this.getAttribute('content-path')}`);

        let event = new CustomEvent('nav-item-clicked-event', {
            composed: true,
            bubbles: true,
            cancelable: true,
            detail: {
                name: this.getAttribute('name'),
                contentPath: this.getAttribute('content-path'),
            }
        });
        // Emit the event
        this.dispatchEvent(event);
        //this.render(); // Re-render to update the active state
    }

    disconnectedCallback() {
        this.navItem.removeEventListener('click', this.handleNavClick);
        delete this.navItem;
        //this._parent.removeEventListener("click", this);
        //delete this._parent;
    }

    attributeChangedCallback(name, oldValue, newValue) {
        //console.log(`NavItem Attribute ${name} changed from ${oldValue} to ${newValue}`);
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
    color: #333;
    font-weight: bold;
}
</style>
<span class='nav-item'>${this.textContent}</span>`;

    }

    //handleEvent(e) {
    //    // Run code on click
    //    console.log('Handle click event');
    //    let event = new CustomEvent('my-custom-event', {
    //        bubbles: false,
    //        cancelable: true,
    //        detail: 'This is awesome. I could also be an object or array.'
    //    });
    //    // Emit the event
    //    this.dispatchEvent(event);

    //}
}


let event = new CustomEvent('navigation-changed-event', {
    composed: true,
    bubbles: true,
    cancelable: true,
    detail: 'Some navigation-changed-event . This is awesome. I could also be an object or array.'
});

class SiteNavigationBar extends HTMLElement {
    //static observedAttributes = ["color", "size"];

    constructor() {
        super(); // Always call super first in constructor
        this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
        this.render();
        this.addEventListener('nav-item-clicked-event', function (event) {
            console.log('event-detail:', event.detail);

            // Emit the event
            document.dispatchEvent(new CustomEvent('navigation-changed-event', {
                composed: true,
                bubbles: true,
                cancelable: true,
                detail: 'Some navigation-changed-event . This is awesome. I could also be an object or array.'
            }));
        });
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
    nav-item[active='true'] {
        color: #fff275;
        font-weight: bold;
    }
</style>
<nav>
    <nav-item name='home'   content-path='./content0.js' active='true'>Home</nav-item>
    <nav-item name='page-1' content-path='./content1.js'>Page 1</nav-item>
    <nav-item name='page-2' content-path='./content2.js'>Page 2</nav-item>
</nav>`;
    }
}


// Define the custom elements

customElements.define('nav-item', NavItem);
customElements.define('site-navigation-bar', SiteNavigationBar);
