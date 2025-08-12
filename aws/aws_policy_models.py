"""
AWS Policy data structures using Pydantic for better type safety and validation.
"""
from typing import Dict, List, Union, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum

class Effect(str, Enum):
    ALLOW = "Allow"
    DENY = "Deny"

class Principal(BaseModel):
    """Represents a principal in an AWS policy statement."""
    AWS: Optional[Union[str, List[str]]] = None
    Service: Optional[Union[str, List[str]]] = None
    Federated: Optional[Union[str, List[str]]] = None
    CanonicalUser: Optional[Union[str, List[str]]] = None

class PolicyStatement(BaseModel):
    """Represents a single statement in an AWS policy document."""
    Sid: Optional[str] = None
    Effect: Effect
    Principal: Optional[Union[str, Dict[str, Any]]] = None
    NotPrincipal: Optional[Union[str, Dict[str, Any]]] = None
    Action: Optional[Union[str, List[str]]] = None
    NotAction: Optional[Union[str, List[str]]] = None
    Resource: Optional[Union[str, List[str]]] = None
    NotResource: Optional[Union[str, List[str]]] = None
    Condition: Optional[Dict[str, Dict[str, Union[str, List[str]]]]] = None

class PolicyDocument(BaseModel):
    """Represents an AWS policy document."""
    Version: str = Field(default="2012-10-17")
    Id: Optional[str] = None
    Statement: List[PolicyStatement]
    
    def to_dict(self) -> dict:
        """Convert to dictionary format expected by boto3."""
        return self.model_dump(exclude_none=True)
    
    def to_json(self) -> str:
        """Convert to JSON string format expected by boto3."""
        import json
        return json.dumps(self.to_dict())

class SQSPolicyBuilder:
    """Builder class for common SQS policies."""
    
    @staticmethod
    def allow_sns_send_message(queue_arn: str, topic_arn: str, sid: str = "AllowSNSToSendMessage") -> PolicyDocument:
        """Create a policy that allows SNS to send messages to an SQS queue."""
        statement = PolicyStatement(
            Sid=sid,
            Effect=Effect.ALLOW,
            Principal=Principal(Service="sns.amazonaws.com"),
            Action="sqs:SendMessage",
            Resource=queue_arn,
            Condition={
                "ArnEquals": {
                    "aws:SourceArn": topic_arn
                }
            }
        )
        
        return PolicyDocument(Statement=[statement])

class SNSPolicyBuilder:
    """Builder class for common SNS policies."""
    
    @staticmethod
    def allow_publish_from_role(topic_arn: str, role_arn: str, sid: str = "AllowRoleToPublish") -> PolicyDocument:
        """Create a policy that allows a role to publish to an SNS topic."""
        statement = PolicyStatement(
            Sid=sid,
            Effect=Effect.ALLOW,
            Principal={"AWS": role_arn},
            Action="sns:Publish",
            Resource=topic_arn
        )
        
        return PolicyDocument(Statement=[statement])

# Example usage functions
def create_sns_sqs_policy_example():
    """Example of creating an SNS->SQS policy using the builder."""
    queue_arn = "arn:aws:sqs:us-east-1:123456789012:example-queue"
    topic_arn = "arn:aws:sns:us-east-1:123456789012:example-topic"
    
    policy = SQSPolicyBuilder.allow_sns_send_message(queue_arn, topic_arn)
    
    # Get as dictionary for boto3
    policy_dict = policy.to_dict()
    print("Policy as dict:", policy_dict)
    
    # Get as JSON string for boto3
    policy_json = policy.to_json()
    print("Policy as JSON:", policy_json)
    
    return policy_dict

if __name__ == "__main__":
    create_sns_sqs_policy_example()
