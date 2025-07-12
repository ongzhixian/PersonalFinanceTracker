import { BASE_API_GATEWAY_ENDPOINT_URL, AuthenticationModule } from '../../components/shared_module.js';

export default function RoleModule() {

    this.authenticationModule = new AuthenticationModule();

    this.registerRole = async (registrationDetail) => {
        // Simulate response
        await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate network delay
        return {
            is_success: true,
            message: `${registrationDetail.name} exists already`,
            data_object: null
        };

        const jwt = this.authenticationModule.getToken();
        if (jwt === null)
            return {
                is_success: false,
                message: `No authentication token found. Please log in first.`,
                data_object: null
            };
        const endpoint_url = `${BASE_API_GATEWAY_ENDPOINT_URL}/role`;
        const response = await fetch(endpoint_url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${jwt}`
            },
            body: JSON.stringify(registrationDetail)
        });
        if (!response.ok) throw new Error("Registration failed: " + response.statusText);
        return await response.json();
    }
}