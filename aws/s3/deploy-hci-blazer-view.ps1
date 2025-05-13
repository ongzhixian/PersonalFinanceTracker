#
aws s3 sync .\hci-blazer-view\ s3://hci-blazer-view/
# URL
# s3-website dash (-) Region ‐ http://bucket-name.s3-website-Region.amazonaws.com
# s3-website dot  (.) Region ‐ http://bucket-name.s3-website.Region.amazonaws.com

# s3-website dash (-) Region ‐ http://hci-blazer-view.s3-website-us-east-1.amazonaws.com
# s3-website dot  (.) Region ‐ http://hci-blazer-view.s3-website.us-east-1.amazonaws.com
# python.exe -m http.server --directory .\hci-blazer-view\ 4400