import RoleModule from "./role-module.js";
import { UiModule } from "../../components/shared_module.js";

class RolesTable extends HTMLElement {

    static observedAttributes = ["state"];
    // Applicable state
    // LOADING
    // LOADED

    data = null;

    #roleModule;
    #uiModule;

    constructor() {
        super();
        this.#roleModule = new RoleModule();
        this.#uiModule = new UiModule();
        this.attachShadow({ mode: 'open' });
        this.handlePaginationClick = this.handlePaginationClick.bind(this);
    }

    connectedCallback() {
        this.template = this.#uiModule.get_template_or_throw('rolesTableTemplate')
        this.getData();
    }

    async getData(page_number = 1, page_size = 5) {
        const auth_module = new AuthenticationModule();
        //const endpoint_url = `https://7pps9elf11.execute-api.us-east-1.amazonaws.com/user-credential?page_number=${page_number}&page_size=${page_size}`;
        const endpoint_url = `https://7pps9elf11.execute-api.us-east-1.amazonaws.com/role`;
        const requestHeaders = new Headers({
            "Content-Type": "application/json",
            "Authorization": `TOKEN ${auth_module.getToken()}`
        });

        try {
            this.setAttribute('state', 'LOADING');
            // const registrationResponse = await this.#roleModule.registerRole(registrationDetail);

            // const response = await fetch(endpoint_url, {
            //     method: "GET",
            //     headers: requestHeaders
            // });



            // const response = await this.#roleModule.getRoleListAsync();
            // if (response.status === 401) {
            //     auth_module.logout();
            //     window.location.reload();
            //     return;
            // }
            // if (!response.ok) throw new Error("Fetch failed: " + response.statusText);

            // const responseJsonData = await response.json();

            const responseJsonData = await this.#roleModule.getRoleListAsync();
            this.data = responseJsonData.data_object || {};
            this.setAttribute('state', 'LOADED');
            console.log('Fetched data:', this.data);

        } catch (e) {
            console.error(e);
            this.data = {};
        }

        this.render();
    }

    handlePaginationClick(e) {
        if (e.target.classList.contains('pagination-link')) {
            e.preventDefault();
            const page = parseInt(e.target.getAttribute('data-page'), 10);
            const pageSize = this.data?.page_size ?? 5;
            this.getData(page, pageSize);
        }
    }

    render() {
        if (!this.template) return;
        this.shadowRoot.innerHTML = ""; // Clear previous content

        let page_items = Object.entries(this.data.roles ?? {}).map(([key, value]) => {
            value.id ||= key;
            return value;
        });

        const gbFormatter = new Intl.DateTimeFormat('en-GB');
        const rows = Array.isArray(page_items) && page_items.length
            ? page_items.map(item => `
                <tr>
                    <td>${item.name ?? ''}</td>
                    <td>${item.description ?? ''}</td>
                    <td>${item.status ?? ''}</td>
                </tr>
            `).join('')
            : '<tr><td colspan="4">No data available</td></tr>';


        const clone = this.template.content.cloneNode(true);
        const tbody = clone.querySelector('tbody');
        if (tbody) {
            tbody.innerHTML = rows;
        }
        this.shadowRoot.appendChild(clone);

        // Use event delegation for pagination links
        const rightDiv = this.shadowRoot.querySelector('.right');
        if (rightDiv) {
            rightDiv.removeEventListener('click', this.handlePaginationClick);
            rightDiv.addEventListener('click', this.handlePaginationClick);
        }
    }
}

customElements.define('roles-table', RolesTable);
