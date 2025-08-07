"""
Advanced AWS Policy examples showing different approaches for better policy management.
"""
import json
from typing import Dict, List
from dataclasses import dataclass, asdict
from aws_policy_models import PolicyDocument, PolicyStatement, Effect, SQSPolicyBuilder

# Approach 3: Using dataclasses (lighter than Pydantic)
@dataclass
class SimplePolicy:
    version: str = "2012-10-17"
    statements: List[Dict] = None
    
    def __post_init__(self):
        if self.statements is None:
            self.statements = []
    
    def add_statement(self, statement: Dict):
        self.statements.append(statement)
    
    def to_dict(self) -> Dict:
        return {
            "Version": self.version,
            "Statement": self.statements
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())

# Approach 4: Policy Builder Pattern (Fluent Interface)
class FluentPolicyBuilder:
    """Fluent interface for building AWS policies."""
    
    def __init__(self):
        self.policy_doc = {
            "Version": "2012-10-17",
            "Statement": []
        }
    
    def add_statement(self, sid: str = None, effect: str = "Allow"):
        statement = {"Effect": effect}
        if sid:
            statement["Sid"] = sid
        self.policy_doc["Statement"].append(statement)
        return StatementBuilder(self, len(self.policy_doc["Statement"]) - 1)
    
    def build(self) -> Dict:
        return self.policy_doc.copy()
    
    def build_json(self) -> str:
        return json.dumps(self.build())

class StatementBuilder:
    """Builder for individual policy statements."""
    
    def __init__(self, policy_builder: FluentPolicyBuilder, statement_index: int):
        self.policy_builder = policy_builder
        self.statement_index = statement_index
    
    @property
    def statement(self):
        return self.policy_builder.policy_doc["Statement"][self.statement_index]
    
    def principal(self, **kwargs):
        """Add principal (Service, AWS, Federated, etc.)"""
        self.statement["Principal"] = kwargs
        return self
    
    def action(self, actions):
        """Add actions (can be string or list)"""
        self.statement["Action"] = actions if isinstance(actions, list) else [actions]
        return self
    
    def resource(self, resources):
        """Add resources (can be string or list)"""
        self.statement["Resource"] = resources if isinstance(resources, list) else [resources]
        return self
    
    def condition(self, condition_dict):
        """Add conditions"""
        self.statement["Condition"] = condition_dict
        return self
    
    def and_statement(self, sid: str = None, effect: str = "Allow"):
        """Add another statement to the policy"""
        return self.policy_builder.add_statement(sid, effect)
    
    def build(self) -> Dict:
        """Build the complete policy"""
        return self.policy_builder.build()
    
    def build_json(self) -> str:
        """Build the complete policy as JSON"""
        return self.policy_builder.build_json()

# Approach 5: Template-based policies with parameter substitution
class PolicyTemplates:
    """Pre-defined policy templates with parameter substitution."""
    
    SNS_TO_SQS_TEMPLATE = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowSNSToSendMessage",
                "Effect": "Allow",
                "Principal": {
                    "Service": "sns.amazonaws.com"
                },
                "Action": "sqs:SendMessage",
                "Resource": "{queue_arn}",
                "Condition": {
                    "ArnEquals": {
                        "aws:SourceArn": "{topic_arn}"
                    }
                }
            }
        ]
    }
    
    LAMBDA_EXECUTION_ROLE_TEMPLATE = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    @classmethod
    def sns_to_sqs_policy(cls, queue_arn: str, topic_arn: str) -> Dict:
        """Generate SNS to SQS policy with parameter substitution."""
        policy_str = json.dumps(cls.SNS_TO_SQS_TEMPLATE)
        policy_str = policy_str.replace("{queue_arn}", queue_arn)
        policy_str = policy_str.replace("{topic_arn}", topic_arn)
        return json.loads(policy_str)
    
    @classmethod
    def lambda_execution_role_policy(cls) -> Dict:
        """Generate Lambda execution role policy."""
        return cls.LAMBDA_EXECUTION_ROLE_TEMPLATE.copy()

# Example usage and comparison
def demonstrate_policy_approaches():
    """Demonstrate different approaches to AWS policy creation."""
    
    queue_arn = "arn:aws:sqs:us-east-1:123456789012:example-queue"
    topic_arn = "arn:aws:sns:us-east-1:123456789012:example-topic"
    
    print("=== 1. Traditional Dictionary Approach ===")
    traditional_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowSNSToSendMessage",
                "Effect": "Allow",
                "Principal": {
                    "Service": "sns.amazonaws.com"
                },
                "Action": "sqs:SendMessage",
                "Resource": queue_arn,
                "Condition": {
                    "ArnEquals": {
                        "aws:SourceArn": topic_arn
                    }
                }
            }
        ]
    }
    print(json.dumps(traditional_policy, indent=2))
    
    print("\n=== 2. Pydantic Model Approach ===")
    pydantic_policy = SQSPolicyBuilder.allow_sns_send_message(queue_arn, topic_arn)
    print(pydantic_policy.to_json())
    
    print("\n=== 3. Dataclass Approach ===")
    dataclass_policy = SimplePolicy()
    dataclass_policy.add_statement({
        "Sid": "AllowSNSToSendMessage",
        "Effect": "Allow",
        "Principal": {"Service": "sns.amazonaws.com"},
        "Action": "sqs:SendMessage",
        "Resource": queue_arn,
        "Condition": {
            "ArnEquals": {"aws:SourceArn": topic_arn}
        }
    })
    print(dataclass_policy.to_json())
    
    print("\n=== 4. Fluent Builder Approach ===")
    fluent_policy = (FluentPolicyBuilder()
                    .add_statement("AllowSNSToSendMessage", "Allow")
                    .principal(Service="sns.amazonaws.com")
                    .action("sqs:SendMessage")
                    .resource(queue_arn)
                    .condition({
                        "ArnEquals": {"aws:SourceArn": topic_arn}
                    })
                    .build_json())
    print(fluent_policy)
    
    print("\n=== 5. Template Approach ===")
    template_policy = PolicyTemplates.sns_to_sqs_policy(queue_arn, topic_arn)
    print(json.dumps(template_policy, indent=2))

if __name__ == "__main__":
    demonstrate_policy_approaches()
