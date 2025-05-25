class SiteBanner extends HTMLElement {
    //static observedAttributes = ["color", "size"];

    constructor() {
        super(); // Always call super first in constructor
        this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
        //console.log("SiteBanner added to page.");
        this.render();
    }

    disconnectedCallback() {
        //console.log("SiteBanner removed from page.");
    }

    connectedMoveCallback() {
        //console.log("SiteBanner moved with moveBefore()");
    }

    adoptedCallback() {
        //console.log("SiteBanner moved to new page.");
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
</style>
<h1>UCM</h1>`;
    }

}

customElements.define('site-banner', SiteBanner);
