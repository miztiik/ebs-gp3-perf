from aws_cdk import aws_ssm as _ssm
from aws_cdk import core


class GlobalArgs():
    """
    Helper to define global statics
    """

    OWNER = "MystiqueAutomation"
    ENVIRONMENT = "production"
    REPO_NAME = "ebs-gp3-perf"
    SOURCE_INFO = f"https://github.com/miztiik/{REPO_NAME}"
    VERSION = "2020_12_11"
    MIZTIIK_SUPPORT_EMAIL = ["mystique@example.com", ]


class CreateSsmRunCommandDocument(core.Construct):

    def __init__(
        self,
        scope: core.Construct,
        construct_id: str,
        run_document_name: str,
        _doc_desc: str,
        bash_commands_to_run: str,
        enable_log: bool,
        **kwargs
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)

        # SSM Run Command Document should be JSON Syntax
        # Ref: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-document.html#cfn-ssm-document-content
        # Ref: https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ssm/CfnDocument.html
        _run_cmds = {
            "schemaVersion": "2.2",
            "description": f"{_doc_desc}",
            "parameters": {
                "commands": {
                    "type": "String",
                    "description": "The commands to run or the path to an existing script on the instance.",
                    "default": f"{bash_commands_to_run}"
                }
            },
            "mainSteps": [
                {
                    "action": "aws:runShellScript",
                    "name": "runCommands",
                    "inputs": {
                        "timeoutSeconds": "600",
                        "runCommand": [
                            "{{ commands }}"
                        ]
                    }
                }
            ]
        }

        # Create Linux Shell Script Document
        self.ssm_linux_document = _ssm.CfnDocument(
            self,
            "ssmLinuxDocument",
            document_type="Command",
            # If we name in Cfn, Updating becomes a problem
            # name=f"{run_document_name}",
            content=_run_cmds
        )

    # properties to share with other stacks
    @property
    def get_ssm_linux_document_name(self):
        return self.ssm_linux_document.ref
