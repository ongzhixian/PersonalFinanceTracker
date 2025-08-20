import {
    BASE_API_GATEWAY_ENDPOINT_URL,
    AuthenticationModule,
    Http401Unauthorized,
    notOkResponse,
    HttpModule
} from '../../components/shared_module.js';

export default function RoleModule(httpModule = new HttpModule()) {

    const CACHE_KEY = "roleListCache";
    const CACHE_TIMESTAMP_KEY = "roleListCacheTimestamp";
    const CACHE_DURATION_MS = 1 * 60 * 1000; // 1 minute
    const ROLE_ENDPOINT_URL = `${BASE_API_GATEWAY_ENDPOINT_URL}/role`;

    this.authenticationModule = new AuthenticationModule();
    this.httpModule = httpModule;

    const getJwtOrError = () => {
        const jwt = this.authenticationModule.getToken();
        if (!jwt) {
            return {
                error: true,
                response: {
                    is_success: false,
                    message: "No authentication token found. Please log in first.",
                    data_object: null
                }
            };
        }
        return { error: false, jwt };
    };

    this.getRequestHeaders = () => {
        // const {error, jwt, response} = getJwtOrError();
        // if (error) return response;
        const jwt = this.authenticationModule.getToken();
        return {
            "Content-Type": "application/json",
            "Authorization": `TOKEN ${jwt}`
        }
    }

    this.registerRole = async (registrationDetail) => {
        try
        {
            const response = await fetch(ROLE_ENDPOINT_URL, {
                method: "POST",
                headers: this.httpModule.getRequestHeaders(),
                body: JSON.stringify(registrationDetail)
            });

            if (response.ok) return await response.json();

            return notOkResponse(response)

            // if (!response.ok) throw new Error("Registration failed: " + response.statusText);
            // return await response.json();
            // if (response.status === 401) {
            //     auth_module.logout();
            //     window.location.reload();
            //     return;
            // }
        }
        catch (error) {
            if (error instanceof Http401Unauthorized) {
                this.authenticationModule.logout();
                window.location.reload();
                return;
            }
            console.error("Error during role registration:", error);
            return {
                is_success: false,
                message: "An unexpected error occurred during registration.",
                data_object: null
            };
        }

        // Simulate response
        //await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate network delay
        //return {
        //    is_success: true,
        //    message: `${registrationDetail.name} exists already`,
        //    data_object: null
        //};

        // const jwt = this.authenticationModule.getToken();
        // if (jwt === null)
        //     return {
        //         is_success: false,
        //         message: `No authentication token found. Please log in first.`,
        //         data_object: null
        //     };

        // const { error, jwt, response } = getJwtOrError();
        // if (error) return response;

        // const endpoint_url = `${BASE_API_GATEWAY_ENDPOINT_URL}/role`;
        // const response = await fetch(ROLE_ENDPOINT_URL, {
        //     method: "POST",
        //     headers: {
        //         "Content-Type": "application/json",
        //         "Authorization": `TOKEN ${jwt}`
        //     },
        //     body: JSON.stringify(registrationDetail)
        // });
        //
        // if (!response.ok) throw new Error("Registration failed: " + response.statusText);
        // return await response.json();
    }

    this.getRoleListAsync = async () => {

        const now = Date.now();
        const cachedData = localStorage.getItem(CACHE_KEY);
        const cachedTimestamp = localStorage.getItem(CACHE_TIMESTAMP_KEY);

        if (cachedData && cachedTimestamp && (now - cachedTimestamp < CACHE_DURATION_MS)) {
            console.info("Using cached role list data.");
            return JSON.parse(cachedData);
        }

        // const { error, jwt, response } = getJwtOrError();
        // if (error) return response;

        // const jwt = this.authenticationModule.getToken();
        //
        // if (jwt === null)
        //     return {
        //         is_success: false,
        //         message: `No authentication token found. Please log in first.`,
        //         data_object: null
        //     };

        // const endpoint_url = `${BASE_API_GATEWAY_ENDPOINT_URL}/role`;

        try
        {

            // if (response.status === 401) {
            //     auth_module.logout();
            //     window.location.reload();
            //     return;
            // }

            // if (!response.ok) throw new Error("Fetch failed: " + response.statusText);


            // return await response.json();
            // if (!response.ok) throw new Error("Registration failed: " + response.statusText);
            // return await response;

            console.info("Fetching role list data.");
            const response = await fetch(ROLE_ENDPOINT_URL, {
                method: "GET",
                headers: this.httpModule.getRequestHeaders()
                //this.getRequestHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem(CACHE_KEY, JSON.stringify(data));
                localStorage.setItem(CACHE_TIMESTAMP_KEY, now.toString());
                return data;
            }

            console.warning("Error getting role list.", response.statusText);
            return notOkResponse(response)
            // return notOkResponse;

        }
        catch (error) {
            // if (error instanceof Http401Unauthorized) {
            //     this.authenticationModule.logout();
            //     window.location.reload();
            //     return;
            // }

            if (error instanceof Http401Unauthorized)
                return (() => { this.authenticationModule.logout(); location.reload(); })();

            throw error;
        }

    }

    function handleUnauthorized() {
        this.authenticationModule.logout();
        location.reload();
    }

}
