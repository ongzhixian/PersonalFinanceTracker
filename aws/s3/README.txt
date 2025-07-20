# Notes
Copy bucket to local folder
aws s3 sync s3://emptool-public/ C:\src\github.com\ongzhixian\pft-aws\aws\s3\emptool-public


## CloudFront

### Add an alternate domain name

Let's say you want to add `cdn.emptool.com` as an alternate domain name for your CloudFront distribution. 
You would do the following:

1.  Go to AWS Certificate Manager and request a public certificate for `cdn.emptool.com`.
    Just follow the steps to validate the domain ownership.
    1. Enter the fully qualified domain name (FQDN) as `cdn.emptool.com`.
    2. Accept the defaults and click "Request".

    You will see a message like this:

    Successfully requested certificate with ID 96e61fb8-847c-4cf8-82bb-a5ce80ca3225
    A certificate request with a status of pending validation has been created. 
    Further action is needed to complete the validation and approval of the certificate.

    In the certificates screen under the "Domains" section, you will see the domain name and status as "Pending validation".
    Copy the CNAME record name and value.
    _62f955870e0c01a462e18bf714d04dd2.cdn.emptool.com.
    _c7a0ba2b7ae571537140305dbe076d96.xlfgrmvvlj.acm-validations.aws.

2.  Go to DNS (Route 53 or GoDaddy) and create:
    1.  a new CNAME record set for `cdn.emptool.com`.
    2.  a new CNAME record set for the name and value copied from the certificate request.


3.  Go to AWS Certificate Manager and check the status of the certificate.

    This can take some time (half an hour or more?).

    Unfortunately, there doesn't seems to be any way no way to speed this up.


4.  Once the status is "Issued", you can go to CloudFront and add the alternate domain name.

    1.  Add `cdn.emptool.com` to the "Alternate Domain Names (CNAMEs)" field.
    2.  Select the certificate you just created from the "SSL Certificate" dropdown.
    3.  Click "Save Changes".

