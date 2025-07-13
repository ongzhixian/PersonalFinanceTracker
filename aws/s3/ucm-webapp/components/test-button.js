class TestButton extends HTMLElement {
    //static observedAttributes = ["color", "size"];
    displayTarget = null;

    constructor() {
        super(); // Always call super first in constructor
        this.attachShadow({ mode: 'open' });
        this.channelHandler = new ChannelHandler('test-button');

        // this.broadcastChannel = new BroadcastChannel("test_channel");
        // this.broadcastChannel.onmessage = function(event) {
        //     console.log('testButton', event.data);
        // }
    }

    #runTestButtonClick(e) {
        if ( (this.displayTarget === null) || this.displayTarget === 'test-content2' ) {
            this.displayTarget = 'test-content1';
        } else {
            this.displayTarget = 'test-content2';
        }

        this.channelHandler.sendMessage({
            type: 'display',
            targetId: this.displayTarget
        });
        // this.channelHandler.sendMessage('Hello world')
    }

    connectedCallback() {
        //console.log("SiteBanner added to page.");
        this.render();
        this.shadowRoot.querySelector('#runTestButton').addEventListener('click', (e) => this.#runTestButtonClick(e));
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
<style></style>
<button id="runTestButton">Run test</button>
`;
    }

}

customElements.define('test-button', TestButton);
