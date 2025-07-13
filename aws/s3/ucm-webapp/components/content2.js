class TestContent2 extends HTMLElement {
    //static observedAttributes = ["color", "size"];

    constructor() {
        super(); // Always call super first in constructor
        this.attachShadow({ mode: 'open' });
        this.channelHandler = new ChannelHandler('content2');
        this.channelHandler.subscribe((e) => this.onmessage(e));

        // this.broadcastChannel = new BroadcastChannel("test_channel");
        // this.broadcastChannel.onmessage = function(event) {
        //     console.log('SiteBanner', event.data);
        // }
    }

    onmessage = function(event) {
        // this.shadowRoot.querySelector('h1').innerText = event.data;
        if ( (event.data.type === 'display') && (event.data.targetId === 'test-content2') ) {
            this.classList.remove('hide')
        } else {
            this.classList.add('hide');
        }
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
<h1>Test Content 2</h1>`;
    }

}

customElements.define('test-content2', TestContent2);
