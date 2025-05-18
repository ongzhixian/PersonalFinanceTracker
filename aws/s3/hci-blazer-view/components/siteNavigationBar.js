class SiteNavigationBar extends HTMLElement {
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
          <li><a href="/" class="${currentPage === '/' ? 'active' : ''}">Home</a></li>
          <li><a href="/reports/inventory-overview.html" class="${currentPage === '/reports/inventory-overview.html' ? 'active' : ''}">Inventory-Overview</a></li>
          <li><a href="/reports/inventory-list.html" class="${currentPage === '/reports/inventory-list.html' ? 'active' : ''}">Inventory-List</a></li>
          <li><a href="/reports/inventory-query.html" class="${currentPage === '/reports/inventory-query.html' ? 'active' : ''}">Inventory-Query</a></li>
          <!--
          <li><a href="/reports/inventory.html" class="${currentPage === '/reports/inventory.html' ? 'active' : ''}" disabled>Due Soon</a></li>
          <li><a href="/reports/inventory.html" class="${currentPage === '/reports/inventory.html' ? 'active' : ''}">Outstanding</a></li>
          -->
        </ul>
      </nav>
    `;
    }
}

customElements.define('site-navigation-bar', SiteNavigationBar);