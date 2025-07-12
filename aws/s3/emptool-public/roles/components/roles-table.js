class RolesTable extends HTMLElement {

    static observedAttributes = ["state"];
    // Applicable state
    // LOADING
    // LOADED


    data = null;

    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.handlePaginationClick = this.handlePaginationClick.bind(this);
    }

    connectedCallback() {
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
            const response = await fetch(endpoint_url, {
                method: "GET",
                headers: requestHeaders
            });

            if (response.status === 401) {
                auth_module.logout();
                window.location.reload();
                return;
            }

            if (!response.ok) throw new Error("Fetch failed: " + response.statusText);

            const responseJsonData = await response.json();
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
            const pageSize = this.data?.page_size || 5;
            this.getData(page, pageSize);
        }
    }

    render() {
        let page_items = Object.entries(this.data.roles).map(([key, value]) => {
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

        this.shadowRoot.innerHTML = `
<style>
table {
    width: 100%;
}
th, td {
    padding: 12px 15px;
    text-align: left;
    border-bottom: 1px solid #E1E1E1;
}
/* Loading Spinner Styles */
.loading-spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid var(--color3);
    border-radius: 50%;
    width: 20px;
    height: 20px;
    animation: spin 1s linear infinite;
    display: inline-block;
    vertical-align: middle;
    margin-right: 8px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
</style>
<section class="actions panel">
    <a class="button button-primary" href="add-role.html">Add role</a>
</section>
<section>
    <table>
        <caption>Role list</caption>
        <thead>
            <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            ${rows}
        </tbody>
    </table>
</section>
`;

        // Use event delegation for pagination links
        const rightDiv = this.shadowRoot.querySelector('.right');
        if (rightDiv) {
            rightDiv.removeEventListener('click', this.handlePaginationClick);
            rightDiv.addEventListener('click', this.handlePaginationClick);
        }
    }
}

customElements.define('roles-table', RolesTable);