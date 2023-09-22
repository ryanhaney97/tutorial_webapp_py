from aws_cdk import (
    Stack,
    aws_s3_assets as s3_assets,
    aws_elasticbeanstalk as ebs,
    aws_iam as iam
)
from constructs import Construct


class EbApplnStack(Stack):
    def __init__(self, scope: Construct, construct_id: str,
                 min_size="1", max_size="1", instance_types="t2.micro",
                 env_name="MyWebAppEnvironment", **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        web_app_zip_archive = s3_assets.Asset(self, "WebAppZip",
                                              path="./src"
                                              )
        app_name = "MyWebApp"
        app = ebs.CfnApplication(self, "Application",
                                 application_name=app_name
                                 )
        app_version = ebs.CfnApplicationVersion(self, "AppVersion",
                                                application_name=app_name,
                                                source_bundle=ebs.CfnApplicationVersion.SourceBundleProperty(
                                                    s3_bucket=web_app_zip_archive.s3_bucket_name,
                                                    s3_key=web_app_zip_archive.s3_object_key
                                                ))
        app_version.add_dependency(app)

        my_role = iam.Role(self, f"{app_name}-aws-elasticbeanstalk-ec2-role",
                           assumed_by=iam.ServicePrincipal("ec2.amazonaws.com")
                           )
        managed_policy = iam.ManagedPolicy.from_aws_managed_policy_name("AWSElasticBeanstalkWebTier")
        my_role.add_managed_policy(managed_policy)
        my_profile_name = f"{app_name}-InstanceProfile"
        instance_profile = iam.CfnInstanceProfile(self, my_profile_name,
                                                  instance_profile_name=my_profile_name,
                                                  roles=[my_role.role_name]
                                                  )

        option_setting_properties = [
            ebs.CfnEnvironment.OptionSettingProperty(
                namespace="aws:autoscaling:launchconfiguration",
                option_name="IamInstanceProfile",
                value=my_profile_name
            ),
            ebs.CfnEnvironment.OptionSettingProperty(
                namespace="aws:autoscaling:asg",
                option_name="MinSize",
                value=min_size
            ),
            ebs.CfnEnvironment.OptionSettingProperty(
                namespace="aws:autoscaling:asg",
                option_name="MaxSize",
                value=max_size
            ),
            ebs.CfnEnvironment.OptionSettingProperty(
                namespace="aws:ec2:instances",
                option_name="InstanceTypes",
                value=instance_types
            )
        ]
        elb_env = ebs.CfnEnvironment(self, "Environment",
                                     environment_name=env_name,
                                     application_name=app.application_name if app.application_name else app_name,
                                     solution_stack_name="64bit Amazon Linux 2 v5.8.5 running Node.js 18",
                                     option_settings=option_setting_properties,
                                     version_label=app_version.ref
                                     )
