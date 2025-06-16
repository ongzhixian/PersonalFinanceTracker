class SiteBanner extends HTMLElement {
    //static observedAttributes = ["color", "size"];

    constructor() {
        super(); // Always call super first in constructor
        this.attachShadow({ mode: 'open' });
        this.channelHandler = new ChannelHandler('site-banner');

        // Bind the onMessage method once to avoid creating a new function on every event
        this.boundOnMessage = this.onMessage.bind(this);
        this.channelHandler.subscribe(this.boundOnMessage);

        // Cache for the h1 element
        this._h1 = null;

        // this.broadcastChannel = new BroadcastChannel("test_channel");
        // this.broadcastChannel.onmessage = function(event) {
        //     console.log('SiteBanner', event.data);
        // }
        this.auth_module = new AuthenticationModule();
        this.parsedToken = this.auth_module.getParsedToken();
    }

    onMessage(event) {
        if (event.data?.type === 'setTitle' && event.data.targetId === 'banner' && this._h1) {
            this._h1.textContent = event.data.title;
        }
    }

    connectedCallback() {
        this.render();
        // Cache the h1 element after rendering
        this._h1 = this.shadowRoot.querySelector('h1');
    }

    disconnectedCallback() {
        // Unsubscribe to prevent memory leaks
        if (this.channelHandler && this.boundOnMessage) {
            this.channelHandler.unsubscribe(this.boundOnMessage);
        }
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
        let username = 'Guest';
        let logoutLink = '';

        if (this.parsedToken) {
            username = `Log in as ${this.parsedToken.username || 'Guest'}`;
            logoutLink = '<a href="./logout.html">logout</a>';
        }

        this.shadowRoot.innerHTML = `
<style>
    :host {
        display: block;
        width: 100%;
    }
    .banner-container {
        position: relative;
        display: flex;
        align-items: center;
        height: 8rem;
        background: #f5f5f5;
        box-sizing: border-box;
        padding: 0 1.618rem;
    }
    .banner-left {
        flex: 1 1 auto;
        display: flex;
        align-items: center;
        height: 100%;
    }
    h1 {
        font-size: 4.0rem;
        font-weight: 300;
        margin: 0;
    }
    .banner-top-right, .banner-bottom-right {
        position: absolute;
        right: 32px;
        text-align: right;
        color: #666;
        font-size: 1.2rem;
        font-weight: 400;
        //pointer-events: none;
        //user-select: none;
    }
    .banner-top-right {
        top: 12px;
    }
    .banner-bottom-right {
        bottom: 12px;
    }

    .marquee-container {
        width: 100%;
        overflow: hidden;
        background: #e0e0e0;
        height: 32px;
        display: flex;
        align-items: center;
        box-sizing: border-box;
        border-top: 1px solid #ccc;
    }
    .marquee-text {
        display: inline-block;
        white-space: nowrap;
        will-change: transform;
        animation: marquee 12s linear infinite;
        font-size: 1.2rem;
        color: #333;
        padding-left: 100%;
    }
    @keyframes marquee {
        0% {
            transform: translateX(0);
        }
        100% {
            transform: translateX(-100%);
        }
    }
</style>
<div class="banner-container">
    <div class="banner-left">
        <h1>TEST</h1>
    </div>
    <div class="banner-top-right">${logoutLink}</div>
    <div class="banner-bottom-right">${username}</div>
</div>
<!-- Marquee section 
<div class="marquee-container">
    <span class="marquee-text">Welcome to the site! This is a scrolling marquee message. Stay tuned for updates.</span>
</div>
-->
`;
    }

}

customElements.define('site-banner', SiteBanner);
