import os
from datetime import datetime
import requests
from requests_negotiate_sspi import HttpNegotiateAuth

from utility_types import JwtUtility

# Csid Utility
class CsidUtility(object):
    """
    Utility class for getting CSID (Client-Side ID) information.
    This class retrieves the CSID token from a file or from the API if the token is not available or has expired.
    It also provides a method to read the stored CSID token and check its validity.
    """
    def __init__(self, environment: str = 'UAT', application_name: str = 'CoreDataUAT'):
        self.target_environment = environment.upper()
        self.application_name = application_name
        if self.target_environment not in ['UAT', 'PRODUCTION']:
            raise ValueError("Invalid environment specified. Use 'UAT' or 'PRODUCTION'.")

    def _read_stored_csid_token(self):
        
        token_path = f'./{self.target_environment.lower()}-csid_token.txt'
        print(f"Reading CSID token from file {token_path}...")
        if not os.path.exists(token_path):
            return None

        with open(token_path, 'r', encoding='utf-8') as in_file:
            csid_token = in_file.read()

        header, payload, signature = JwtUtility.decode_jwt(csid_token)
        # print("Header:", header, "Payload:", payload, "Signature:", signature)

        expiry_dt = datetime.fromtimestamp(payload['exp'])
        if datetime.now() >= expiry_dt:
            print("CSID token has expired, retrieving a new one from the API.")
            return None

        return csid_token

    def _get_csid_token_from_api(self):
        # It is important to verify the certificate with the MLP CA
        # You can download it from https://ca.mlp.com/certData/ca-bundle.txt
        # https://wiki-pm.mlp.com/display/ISEC/Proxies%3A+Certificate
        
        if self.target_environment == 'UAT':
            csid_token_base_url = "https://cs-identity-uat.mlp.com"
        if self.target_environment == 'PRODUCTION':
            csid_token_base_url = "https://cs-identity.mlp.com"

        csid_token_url = f"{csid_token_base_url}/api/v2.0/token?applications={self.application_name}"
        print(f"Retrieving {self.target_environment} CSID token for {self.application_name} from API...")

        csid_token_response = requests.get(csid_token_url, auth=HttpNegotiateAuth(), verify="C:/Code/certs/cacerts.pem")
        csid_token_response_json = csid_token_response.json()
        csid_token = csid_token_response_json['token']
        with open(f'{self.target_environment.lower()}-csid_token.txt', 'w', encoding='utf-8') as out_file:
            out_file.write(csid_token)
        return csid_token

    def get_csid_token(self):
        """
        Get the CSID token, either from the stored file or by retrieving it from the API.
        If the token is not available or has expired, it retrieves a new token from the API.
        """
        try:
            csid_token = self._read_stored_csid_token() or self._get_csid_token_from_api()
            if not csid_token:
                print("No CSID token found or could not retrieve it from the API.")
                print("Please ensure you have access to the CSID API and that the token is stored in 'csid_token.txt'.")
                exit(9)
            return csid_token
        except ValueError as e:
            print(f"Error: {e}")
            exit(1)