import { BASE_API_GATEWAY_ENDPOINT_URL, AuthenticationModule } from '../../components/shared_module.js';

export default function UserCredentialModule() {
    this.authenticationModule = new AuthenticationModule();
    this.registerUserCredential = async (username, password) => {

        // Simulate response
        // return {
        //     is_success: true,
        //     message: `${username} exists already`,
        //     data_object: null
        // };

        const jwt = this.authenticationModule.getToken();
        if (jwt === null)
            return {
                is_success: false,
                message: `No authentication token found. Please log in first.`,
                data_object: null
            };

        const endpoint_url = `${BASE_API_GATEWAY_ENDPOINT_URL}/user-credential`;
        const response = await fetch(endpoint_url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${jwt}`
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        if (!response.ok) throw new Error("Registration failed: " + response.statusText);

        return await response.json();
    }
}