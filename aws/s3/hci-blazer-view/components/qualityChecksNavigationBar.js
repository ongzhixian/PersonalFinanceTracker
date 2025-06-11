class QualityChecksSiteNavigationBar extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    static get observedAttributes() {
        return ['name'];
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (name === 'name') {
            this.render();
        }
    }

    connectedCallback() {
        this.render();
    }

    // render() {
    //     const name = this.getAttribute('name') || 'Guest';
    //     this.shadowRoot.innerHTML = `
    //         <style>
    //             :host {
    //                 display: inline-block;
    //                 padding: 10px;
    //                 border: 1px solid #ccc;
    //                 border-radius: 5px;
    //                 background-color: #f9f9f9;
    //             }
    //             .greeting {
    //                 font-weight: bold;
    //                 color: blue;
    //             }
    //         </style>
    //         <div class="greeting">Hello, ${name}!</div>
    //     `;
    // }


    render() {
        const currentPage = window.location.pathname;
        this.shadowRoot.innerHTML = `
      <style>
        nav {
          background-color: #f0f0f0;
          padding: 10px;
        }

        ul {
          list-style: none;
          padding: 0;
          margin: 0;
          display: flex;
          gap: 20px;
        }

        li a {
          text-decoration: underline;
          color: #333;
        }

        li a:hover {
          color: blue;
        }

        li a.active {
          font-weight: bold;
          color: green; /* Or any other highlighting style */
        }
      </style>
      <nav>
        <ul>
          <li><a href="/chk" class="${/^\/chk(\/(index\.html)?)?$/i.test(currentPage) ? 'active' : ''}">Home</a></li>
          <li><a href="/chk/quality-checks.html" class="${/^\/chk\/quality-checks\.html$/i.test(currentPage) ? 'active' : ''}">Quality Checks</a></li>
          <li><a href="/chk/logout.html" class="${/^\/chk\/logout\.html$/i.test(currentPage) ? 'active' : ''}">Log out</a></li>
        </ul>
      </nav>
    `;
    }
}

customElements.define('site-navigation-bar', QualityChecksSiteNavigationBar);