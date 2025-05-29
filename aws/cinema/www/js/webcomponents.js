// Webcomponents

class XxxSeatingBookingPanel extends HTMLElement {
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
  <div><a href="/configurations.html">Configurations</a></div>
</nav>`;
    }

}

class SeatingBookingPanel extends HTMLElement {
    constructor() {
        super();
        this.rootElement = this.attachShadow({ mode: "closed" });
    }

    render() {
        this.rootElement.innerHTML = `
<style>
.flex-panel {
    display: flex;
    flex-direction: column;
    margin: 1rem;
    gap: .6rem;
}
.flex-panel.horizontal {
    flex-direction: row;
    justify-content: space-evenly;
}

.grid {
    display: grid;
}

.grid.booking {
    grid-template-columns: 1fr 5rem;
    align-items: center;
    width: max-content;
    gap: .6rem 1rem;
    align-self: center;
}

h1, h2, h3, h4, h5, h6, label {
    color: var(--color4);
    font-weight: 360;
}

button {
    font-size: 1.3em;
    font-weight: 400;
    font-family: "Raleway", "HelveticaNeue", "Helvetica Neue", Helvetica, Arial, sans-serif;
    background-color: var(--color6);
    border: outset var(--color6);
    color: var(--color1);
    padding: 0.36rem;
    min-width: 8rem;
    cursor: pointer;
}

button:hover {
    border: inset lightblue;
    color: white;
}

input {
    font-size: 1.3em;
    font-weight: 400;
    font-family: "Raleway", "HelveticaNeue", "Helvetica Neue", Helvetica, Arial, sans-serif;
    padding: 0.36rem;
}

input[type=text] {
    outline: 2px var(--color2) solid;
    border: var(--color2);
    text-align: center;
    color: var(--color3);
}

input[type="text"]:disabled {
    color: var(--color4);
    /*outline: none;*/
}

input.center, label.center {
    text-align: center;
}

#bookingPanel {
    width: 480px;
    border: 2px solid var(--color2);
}

#bookingPanel h2 {
    margin-bottom: 0;
    text-align: center;
}

</style>
<section id="bookingPanel" class="flex-panel">

    <h2>Book seats for</h2>

  <div class="flex-panel">
    <label for="titleInput" class="center">Title</label>
    <input type="text" id="titleDisplay" class="center" disabled value="SOMETITLE" />
  </div>

  <div class="grid booking">
    <label for="numberOfSeatsToBookInput">Number of seats to book</label>
    <input type="text" id="numberOfSeatsToBookInput" maxlength="2" />

    <label for="startSeatInput">Start seat</label>
    <input type="text" id="startSeatInput" maxlength="3" />
  </div>

  <div class="action flex-panel horizontal">
    <button id="getSeatingPlanButton">Get</button>
    &nbsp;
    <button id="bookSeatsButton">Book</button>
  </div>

</section>
        `;
    }

    connectedCallback() {
        this.render();
    }
}

customElements.define('seating-booking-panel', SeatingBookingPanel);

//window.customElements.define("my-web-component", MyWebComponent);
