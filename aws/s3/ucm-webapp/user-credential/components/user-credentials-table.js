class UserCredentialTable extends HTMLElement {

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
        const endpoint_url = `https://7pps9elf11.execute-api.us-east-1.amazonaws.com/user-credential?page_number=${page_number}&page_size=${page_size}`;
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
            if (false === responseJsonData?.is_success ?? false) console.warn("Data fetch failed:", responseJsonData.message);
            this.data = responseJsonData.data_object || {};
            this.setAttribute('state', 'LOADED');
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
        const { page_items = [], page_number = 1, page_size = 0, total_items = 0 } = this.data || {};
        const totalPages = page_size > 0 ? Math.ceil(total_items / page_size) : 1;
        const gbFormatter = new Intl.DateTimeFormat('en-GB');

        const rows = Array.isArray(page_items) && page_items.length
            ? page_items.map(item => `
                <tr>
                    <td><a href="view-user-credential.html?username=${item.username ?? ''}">${item.username ?? ''}</a></td>
                    <td>${item.status ?? ''}</td>
                    <td>${item.failed_login_attempts ?? ''}</td>
                    <td>${gbFormatter.format(new Date(item.password_last_changed_datetime)) ?? ''}</td>
                </tr>
            `).join('')
            : '<tr><td colspan="4">No data available</td></tr>';

        const paginationLinks = Array.from({ length: totalPages }, (_, i) => {
            const page = i + 1;
            const pageStr = page.toString().padStart(2, '0');
            const isCurrent = page === page_number;
            return `<a href="#" class="pagination-link${isCurrent ? ' current' : ''}" data-page="${page}">${pageStr}</a>`;
        }).join('');

        this.shadowRoot.innerHTML = `
<style>
.pagination-link {
    margin: 0 0.5rem;
    color: var(--color2);
}
.pagination-link.current {
    font-weight: bold;
    text-decoration: underline;
    color: var(--color3);
}
table {
    width: 100%;
}
table tbody td, table thead th {
    text-align:center;
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
<section>
    <table>
        <caption>User credential list</caption>
        <thead>
            <tr>
                <th>Username</th>
                <th>Status</th>
                <th>Failed Logins</th>
                <th>Last Password Changed</th>
            </tr>
        </thead>
        <tbody>
            ${rows}
        </tbody>
        <tfoot>
            <tr>
                <td colspan="4">
                    <div style="display:flex; justify-content: space-between;">
                        <div class="left">
                            Page ${page_number} of ${totalPages}
                        </div>
                        <div class="right">
                            ${paginationLinks}
                        </div>
                    </div>
                </td>
            </tr>
        </tfoot>
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

customElements.define('user-credentials-table', UserCredentialTable);
