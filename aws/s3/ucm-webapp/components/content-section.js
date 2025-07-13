class ContentSection extends HTMLElement {
    //static observedAttributes = ["color", "size"];

    constructor() {
        super(); // Always call super first in constructor
        this.attachShadow({ mode: 'open' });
        this.channelHandler = new ChannelHandler('content-section');
        this.channelHandler.subscribe((e) => this.onmessage(e));

        // this.broadcastChannel = new BroadcastChannel("test_channel");
        // this.broadcastChannel.onmessage = function(event) {
        //     console.log('SiteBanner', event.data);
        // }
    }

    onmessage = function(event) {
        if ( (event.data.type === 'setTitle') && (event.data.targetId === 'banner') ) {
            this.shadowRoot.querySelector('h1').innerText = event.data.title;
        }
    }

    connectedCallback() {
        
        this.render();
        document.addEventListener('navigation-changed-event', function (event) {
            console.log('navigation-changed-event-detail 22:', event.detail);
        });

        this.contentSection = this.shadowRoot.querySelector('#contentSection');
        import('./content1.js').then(() => {
            this.contentSection.replaceChildren();
            this.contentSection.appendChild(document.createElement('test-content1'));
            contentId = 'test-content1';
        });

        //console.log("Content section rendered.");
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
        this.shadowRoot.innerHTML = `<section id="contentSection">Loading content...</section>`;
    }

}

customElements.define('content-section', ContentSection);
