class CssReplica extends HTMLElement {
    static observedAttributes = ["target-id"];

    shortHandPropertyGroups = [
        {
            property: 'background',
            constituents: [
                'background-attachment', 'background-clip', 'background-color',
                'background-image', 'background-origin', 'background-position',
                'background-repeat', 'background-size'
            ]
        },
        {
            property: 'font',
            constituents: [
                'font-family', 'font-size', 'font-stretch', 'font-style',
                'font-variant', 'font-weight', 'line-height'
            ]
        },
        {
            property: 'border-width',
            constituents: [
                'border-bottom-width', 'border-left-width',
                'border-right-width', 'border-top-width'
            ]
        },
        {
            property: 'border-style',
            constituents: [
                'border-bottom-style', 'border-left-style',
                'border-right-style', 'border-top-style'
            ]
        },
        {
            property: 'border-color',
            constituents: [
                'border-bottom-color', 'border-left-color',
                'border-right-color', 'border-top-color'
            ]
        },
        {
            property: 'border-radius',
            constituents: [
                'border-top-left-radius', 'border-top-right-radius',
                'border-bottom-right-radius', 'border-bottom-left-radius'
            ]
        },
        {
            property: 'border-inline-start',
            constituents: [
                'border-inline-start-color', 'border-inline-start-style', 'border-inline-start-width'
            ]
        },
        {
            property: 'border-inline-end',
            constituents: [
                'border-inline-end-color', 'border-inline-end-style', 'border-inline-end-width'
            ]
        },
        {
            property: 'border-block-start',
            constituents: [
                'border-block-start-color', 'border-block-start-style', 'border-block-start-width'
            ]
        },
        {
            property: 'border-block-end',
            constituents: [
                'border-block-end-color', 'border-block-end-style', 'border-block-end-width'
            ]
        },
        {
            property: 'padding-inline',
            constituents: [
                'padding-inline-start', 'padding-inline-end'
            ]
        },
        {
            property: 'padding-block',
            constituents: [
                'padding-block-start', 'padding-block-end'
            ]
        },
        {
            property: 'text-decoration',
            constituents: [
                'text-decoration-color', 'text-decoration-line',
                'text-decoration-style', 'text-decoration-thickness'
            ]
        },
        {
            property: 'margin',
            constituents: [
                'margin-top', 'margin-right', 'margin-bottom', 'margin-left'
            ]
        },
        {
            property: 'padding',
            constituents: [
                'padding-top', 'padding-right', 'padding-bottom', 'padding-left'
            ]
        }
    ];

    targetId = '';

    constructor() {
        super(); // Always call super first in constructor
        this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
        this.render();
    }

    disconnectedCallback() {
        //console.log("SiteBanner removed from page.");
    }

    connectedMoveCallback() {
        console.log("SiteBanner moved with moveBefore()");
    }

    adoptedCallback() {
        //console.log("SiteBanner moved to new page.");
    }

    attributeChangedCallback(name, oldValue, newValue) {
        console.log(`Attribute ${name} has changed from ${oldValue} to ${newValue}`);
        this.targetId = newValue;
    }

    diffComputedStyleMaps(map1, map2) {
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

    render() {
        console.log('this.targetId', this.targetId);

        const targetElement = document.getElementById(this.targetId);
        if (targetElement === null) {
            console.log('target not found');
            return;
        }

        console.log('targetElement', targetElement);
        this.shadowRoot.innerHTML = targetElement.outerHTML;

        let shadowElement = this.shadowRoot.querySelector(`#${this.targetId }`);
        console.log('shadowElement', shadowElement);

        const targetComputedStyles = targetElement.computedStyleMap();
        const shadowComputedStyles = shadowElement.computedStyleMap();

        let styleDifferences = this.diffComputedStyleMaps(targetComputedStyles, shadowComputedStyles);
        console.log('Number of differences: ', Object.getOwnPropertyNames(styleDifferences).length)
        console.log(styleDifferences);

        let css = [];
        let cssTest = [];
        let sortedStyleDifferencesPropNames = Object.getOwnPropertyNames(styleDifferences).sort();

        for (const { property, constituents } of this.shortHandPropertyGroups) {
            css.push(`${property}: ${targetComputedStyles.get(property).toString()}`);
            cssTest.push({ property, value: targetComputedStyles.get(property).toString() });
            // Remove constituent properties from the list
            const constituentSet = new Set(constituents);
            sortedStyleDifferencesPropNames = sortedStyleDifferencesPropNames.filter(str => !constituentSet.has(str));
        }

        // Handler remaining
        for (const propName of sortedStyleDifferencesPropNames) {
            css.push(`${propName}: ${targetComputedStyles.get(propName).toString()}`);
            cssTest.push({property: propName, value: targetComputedStyles.get(propName).toString()});
        }

        for (const cssTestProp of cssTest) {
            console.log(cssTestProp);
            shadowElement.style[cssTestProp.property] = cssTestProp.value.toString();
        }

        // for (const propName of Object.getOwnPropertyNames(styleDifferences)) {
        //     shadowElement.style[propName] = styleDifferences[propName].target;
        //     css.push(`${propName}: ${styleDifferences[propName].target}`);
        // }

        console.log('Reduced: ', css.length);

    }

}

customElements.define('css-replica', CssReplica);
