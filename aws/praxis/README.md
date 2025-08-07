# Praxis

Praxis: A word meaning "action and practice, as opposed to theory." 

This is a Python workflow for provisioning resources for applications.
The immediate focus is on provisioning resources for AWS.

If it works well, the goal is to extend that capability to other cloud/SaaS resources.

## Goal (or what we are trying to solve here)

Setting up resources on AWS is a chore.
We want to automate the process.

Using the example of setting up a static website, we have to:

1.  Setup S3
2.  Setup CloudFront
3.  Setup DNS

It is tempting to add Api Gateway, Lambda Functions and CI/CD.
But let start


AWS Policies
1.  Static-Content-Delivery
    - S3
    - CloudFront
    - Certificate Manager
2.  Api-Delivery (2nd phase)
    - Api Gateway
    - Lambda

## Project Layout

tests/
docs/
src/
└── praxis/
    ├── __main__.py
    └── main.py
