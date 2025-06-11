function diffComputedStyleMaps(map1, map2) {
    // Get all property names from both maps
    const keys1 = Array.from(map1.keys());
    const keys2 = Array.from(map2.keys());
    const allKeys = Array.from(new Set([...keys1, ...keys2]));

    const differences = {};

    for (const key of allKeys) {
        const val1 = map1.get(key);
        const val2 = map2.get(key);

        // Convert CSSStyleValue to string for comparison
        const str1 = val1 ? val1.toString() : undefined;
        const str2 = val2 ? val2.toString() : undefined;

        if (str1 !== str2) {
          differences[key] = { target: str1, current: str2 };
        }
    }

    return differences;
}

class TestButton extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' }); // 'open' -- makes this.shadowRoot available
        this.handler = new AuthenticationTicketApiHandler();
    }

    static get observedAttributes() {
        return ['name'];
    }

    attributeChangedCallback(name, oldValue, newValue) {
        console.log('Webcomponent event: attributeChangedCallback ');
        if (name === 'name') {
            this.render();
        }
    }


    connectedCallback() {
        console.log('Webcomponent event: connectedCallback ');
        this.render();
        this.shadowRoot.querySelector('button').addEventListener('click', (e) => {
            console.log('test button clicked');
        });

        const button1ComputedStyles = document.querySelectorAll('input[type=button]')[0].computedStyleMap();
        const button2ComputedStyles = document.querySelectorAll('input[type=button]')[1].computedStyleMap();
        const button3ComputedStyles = this.shadowRoot.querySelector('button').computedStyleMap();

        // Compare styles
        let styleDifferences = diffComputedStyleMaps(button1ComputedStyles, button3ComputedStyles);
        console.log('Number of differences: ', Object.getOwnPropertyNames(styleDifferences).length)
        console.log(styleDifferences);
//        let xButton = this.shadowRoot.querySelector('button');
//        let css = [];
//
//        for (const propName of Object.getOwnPropertyNames(styleDifferences)) {
//            xButton.style[propName] = styleDifferences[propName].target;
//            css.push(`${propName}: ${styleDifferences[propName].target}`);
//        }
//
//        debugger;

    }

    render() { // HTML Markup for WebComponent
        // const currentPage = window.location.pathname;
        this.shadowRoot.innerHTML = `
<style>
button.button-primary {
    appearance: button;
    border: 1px solid rgb(51, 195, 240);
    padding: 0px 30px;
    margin: 0px 0px 15px;
    font: 600 11px / 38px Raleway, HelveticaNeue, "Helvetica Neue", Helvetica, Arial, sans-serif;
    text-decoration: none solid rgb(255, 255, 255);
    border: 1px solid rgb(51, 195, 240);
    border-radius: 4px;
    overflow: clip;

    background-color: rgb(51, 195, 240);
    color: rgb(255, 255, 255);

    block-size: 38px;
    cursor: pointer;
    height: 38px;
    letter-spacing: 1px;
    text-transform: uppercase;
    text-wrap-mode: nowrap;
    user-select: none;
}
</style>
<button class="button-primary">Test</button>
`;
    }
}

customElements.define('test-button', TestButton);