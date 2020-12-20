from aws_cdk import aws_ec2 as _ec2
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_ssm as _ssm
from aws_cdk import core

from ebs_gp3_perf.constructs.create_ssm_run_command_document_construct import CreateSsmRunCommandDocument


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


class EbsGp3PerformanceTestStack(core.Stack):

    def __init__(
        self,
        scope: core.Construct, id: str,
        vpc,
        ec2_instance_type: str,
        stack_log_level: str,
        **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # Read BootStrap Script):
        try:
            with open("ebs_gp3_perf/stacks/back_end/bootstrap_scripts/deploy_app.sh",
                      encoding="utf-8",
                      mode="r"
                      ) as f:
                user_data = f.read()
        except OSError as e:
            print("Unable to read UserData script")
            raise e

        # Get the latest AMI from AWS SSM
        amzn_linux_ami = _ec2.MachineImage.latest_amazon_linux(
            generation=_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
        )
        linux_ami_id = _ec2.AmazonLinuxImage(
            generation=_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2).get_image(self).image_id

        # ec2 Instance Role
        _instance_role = _iam.Role(
            self,
            "webAppClientRole",
            assumed_by=_iam.ServicePrincipal(
                "ec2.amazonaws.com"),
            managed_policies=[
                _iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSSMManagedInstanceCore"
                )
            ]
        )

        # Allow CW Agent to create Logs
        _instance_role.add_to_policy(_iam.PolicyStatement(
            actions=[
                "logs:Create*",
                "logs:PutLogEvents"
            ],
            resources=["arn:aws:logs:*:*:*"]
        ))

        # ebs_gp3_perf_server Instance
        self.ebs_gp3_perf_server = _ec2.Instance(
            self,
            "ebsPerfTestServer",
            instance_type=_ec2.InstanceType(
                instance_type_identifier=f"{ec2_instance_type}"),
            instance_name="ebs_gp3_perf_server_01",
            machine_image=amzn_linux_ami,
            vpc=vpc,
            vpc_subnets=_ec2.SubnetSelection(
                subnet_type=_ec2.SubnetType.PUBLIC
            ),
            role=_instance_role,
            user_data_causes_replacement=True,
            user_data=_ec2.UserData.custom(
                user_data),
            # Setting root volume size is not working
            # https://aws.amazon.com/premiumsupport/knowledge-center/cloudformation-root-volume-property/
            # block_devices=[
            #     _ec2.BlockDevice(
            #         device_name="/dev/sda1",
            #         volume=_ec2.BlockDeviceVolume.ebs(
            #             volume_size=30,
            #             encrypted=False,
            #             delete_on_termination=True
            #         )
            #     )
            # ]
        )

        """
            # Cfn NOT SUPPORTING SETTING THROUGHPUT FOR GP3 VOLUMES
            block_devices=[
                _ec2.BlockDevice(
                    device_name="/dev/sdf",
                    volume=_ec2.BlockDeviceVolume.ebs(
                        volume_size=150,
                        iops=4000,
                        volume_type=_ec2.EbsDeviceVolumeType.GP2,
                        encrypted=False,
                        delete_on_termination=True
                    )
                ),
                _ec2.BlockDevice(
                    device_name="/dev/sdg",
                    volume=_ec2.BlockDeviceVolume.ebs(
                        volume_size=150,
                        iops=4000,
                        volume_type=_ec2.EbsDeviceVolumeType.GP2,
                        encrypted=False,
                        delete_on_termination=True
                    )
                ),
                _ec2.BlockDevice(
                    device_name="/dev/sdh",
                    volume=_ec2.BlockDeviceVolume.ebs(
                        volume_size=150,
                        iops=4000,
                        volume_type=_ec2.EbsDeviceVolumeType.GP2,
                        encrypted=False,
                        delete_on_termination=True
                    )
                ),
                _ec2.BlockDevice(
                    device_name="/dev/sdi",
                    volume=_ec2.BlockDeviceVolume.ebs(
                        volume_size=150,
                        iops=4000,
                        volume_type=_ec2.EbsDeviceVolumeType.IO1,
                        encrypted=False,
                        delete_on_termination=True
                    )
                )
            ],
            resource_signal_timeout=core.Duration.minutes(15)



        # CDK does not support GP3, so let us override the block device property
        
        perf_server.add_property_override(
            "BlockDeviceMappings.0.Ebs.VolumeType", "gp3")
        perf_server.add_property_override(
            "BlockDeviceMappings.1.Ebs.VolumeType", "gp3")
        perf_server.add_property_override(
            "BlockDeviceMappings.2.Ebs.VolumeType", "gp3")
        # perf_server.add_property_override(
        #     "BlockDeviceMappings.3.Ebs.VolumeType", "io2")
        """

        perf_server = self.ebs_gp3_perf_server.node.default_child
        # Enabled Detailed Monitoring
        perf_server.monitoring = True

        # Allow EC2 Instance to create and attach volumes & Create Tags
        # https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_ec2_volumes-instance.html
        self.ebs_gp3_perf_server.add_to_role_policy(
            _iam.PolicyStatement(
                actions=[
                    "ec2:CreateVolume",
                    "ec2:AttachVolume",
                    "ec2:DetachVolume",
                    "ec2:DeleteVolume",
                    "ec2:DescribeVolumeAttribute",
                    "ec2:CreateTags"
                ],
                resources=[
                    "arn:aws:ec2:*:*:volume/*",
                    "arn:aws:ec2:*:*:instance/*"
                ],
                conditions={
                    "ArnEquals": {"ec2:SourceInstanceARN": f"arn:aws:ec2:*:*:instance/*"}
                }
            )
        )
        self.ebs_gp3_perf_server.add_to_role_policy(
            _iam.PolicyStatement(
                actions=[
                    "ec2:DescribeVolumes",
                ],
                resources=[
                    "*"
                ]
            )
        )

        # Allow Web Traffic to WebServer
        self.ebs_gp3_perf_server.connections.allow_from_any_ipv4(
            _ec2.Port.tcp(80),
            description="Allow Incoming HTTP Traffic"
        )

        self.ebs_gp3_perf_server.connections.allow_from(
            other=_ec2.Peer.ipv4(vpc.vpc_cidr_block),
            port_range=_ec2.Port.tcp(443),
            description="Allow Incoming FluentBit Traffic"
        )

        # Allow CW Agent to create Logs
        _instance_role.add_to_policy(_iam.PolicyStatement(
            actions=[
                "logs:Create*",
                "logs:PutLogEvents"
            ],
            resources=["arn:aws:logs:*:*:*"]
        ))

        # Because of the cost and the imperfect nature of the script, let us run in manually
        """
        # Read BootStrap Script):
        try:
            with open("../scripts/create_and_attach_volumes.sh",
                      encoding="utf-8",
                      mode="r"
                      ) as f:
                create_and_attach_volumes = f.read()
            with open("../scripts/gp3_throughput_benchmark_with_fio.sh",
                      encoding="utf-8",
                      mode="r"
                      ) as f:
                gp3_throughput_benchmark_with_fio = f.read()
        except OSError as e:
            print("Unable to read bash script")
            raise e

        # Run Volume Creations script using SSM Run Commands using CDK Construct
        create_and_attach_volumes_doc = CreateSsmRunCommandDocument(
            self,
            "gp3AndIo2VolumeCreation",
            run_document_name="gp3AndIo2VolumeCreationScript",
            _doc_desc="Create and Attach gp3 and io2 volumes",
            bash_commands_to_run=create_and_attach_volumes,
            enable_log=False
        )

        # Create SSM Association to trigger SSM doucment to target (EC2)
        _run_volume_creation = _ssm.CfnAssociation(
            self,
            "runVolumeCreationCommandsOnEc2",
            name=create_and_attach_volumes_doc.get_ssm_linux_document_name,
            targets=[{
                "key": "InstanceIds",
                "values": [self.ebs_gp3_perf_server.instance_id]
            }]
        )

        gp3_benchmark_with_fio_doc = CreateSsmRunCommandDocument(
            self,
            "gp3BenchmarkWithFio",
            run_document_name="gp3BenchmarkWithFioScript",
            _doc_desc="Throughput performance benchmarking of gp3 using fio",
            bash_commands_to_run=gp3_throughput_benchmark_with_fio,
            enable_log=False
        )

        # Create SSM Association to trigger SSM doucment to target (EC2)
        _run_fio_tests = _ssm.CfnAssociation(
            self,
            "runCommandsOnEc2",
            name=gp3_benchmark_with_fio_doc.get_ssm_linux_document_name,
            targets=[{
                "key": "InstanceIds",
                "values": [self.ebs_gp3_perf_server.instance_id]
            }]
        )

        # Let us wait until the server is ready, before executing our RunCommand Scripts
        _run_volume_creation.node.add_dependency(
            self.ebs_gp3_perf_server)
        _run_fio_tests.node.add_dependency(self.ebs_gp3_perf_server)
        """

        ###########################################
        ################# OUTPUTS #################
        ###########################################
        output_0 = core.CfnOutput(
            self,
            "AutomationFrom",
            value=f"{GlobalArgs.SOURCE_INFO}",
            description="To know more about this automation stack, check out our github page."
        )
        output_1 = core.CfnOutput(
            self,
            "gp3PerfTestServerIp",
            value=f"http://{self.ebs_gp3_perf_server.instance_private_ip}",
            description=f"Private IP of GP3 Performance Test Server"
        )
        output_2 = core.CfnOutput(
            self,
            "gp3PerfTestInstance",
            value=(
                f"https://console.aws.amazon.com/ec2/v2/home?region="
                f"{core.Aws.REGION}"
                f"#Instances:search="
                f"{self.ebs_gp3_perf_server.instance_id}"
                f";sort=instanceId"
            ),
            description=f"Login to the instance using Systems Manager and use curl to access the Instance"
        )

        output_3 = core.CfnOutput(
            self,
            "WebServerUrl",
            value=f"{self.ebs_gp3_perf_server.instance_public_dns_name}",
            description=f"Public IP of Web Server on EC2"
        )
        output_5 = core.CfnOutput(
            self,
            "GenerateAccessTraffic",
            value=f"ab -n 10 -c 1 http://{self.ebs_gp3_perf_server.instance_public_dns_name}/",
            description=f"Public IP of Web Server on EC2"
        )
        output_6 = core.CfnOutput(
            self,
            "GenerateFailedTraffic",
            value=f"ab -n 10 -c 1 http://{self.ebs_gp3_perf_server.instance_public_dns_name}/${{RANDOM}}",
            description=f"Public IP of Web Server on EC2"
        )

    # properties to share with other stacks
    @property
    def get_inst_id(self):
        return self.ebs_gp3_perf_server.instance_id
