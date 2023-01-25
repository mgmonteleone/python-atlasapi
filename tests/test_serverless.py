"""
Nose2 Unit Tests for the clusters module.


"""
import datetime
from pprint import pprint
from os import environ, getenv
from atlasapi.atlas import Atlas
from atlasapi.projects import Project, ProjectSettings
from atlasapi.teams import TeamRoles
from atlasapi.atlas_users import AtlasUser
from atlasapi.serverless_pydantic import ServerlessInstance, StateName, ServerlessInstanceConnectionStrings, \
    ServerlessInstanceProviderSettings
from json import dumps
from tests import BaseTests
import logging
from time import sleep

logger = logging.getLogger('test')


class ServerlessTests(BaseTests):

    def test_00_get_count_for_group(self):
        count = self.a.Serverless.count_for_group_id(group_id=self.GROUP_ID)
        print(f'✅ There are {count} serverless instances in the project/group.')
        self.assertIsInstance(count, int, "Instance count must be a non-negative int.")

    def test_01_get_instances_for_project(self):
        for each_item in self.a.Serverless.get_all_for_project(group_id=self.GROUP_ID):
            pprint(each_item)
            self.assertIsInstance(each_item, ServerlessInstance)
            self.assertIsInstance(each_item.state_name, StateName)
            self.assertIsInstance(each_item.connection_strings, ServerlessInstanceConnectionStrings)
            self.assertIsInstance(each_item.provider_settings, ServerlessInstanceProviderSettings)
            print(f'✅Checked  serverless instance {each_item.id} for project {each_item.group_id}')

    test_01_get_instances_for_project.basic = True

    def test_02_get_one_instance_for_project(self):
        instance_name = None
        for each_item in self.a.Serverless.get_all_for_project(group_id=self.GROUP_ID):
            instance_name = each_item.name
            break
        instance = self.a.Serverless.get_one_for_project(group_id=self.GROUP_ID, instance_name=instance_name)
        print(instance.dict())
        self.assertIsInstance(instance, ServerlessInstance)

    test_02_get_one_instance_for_project.basic = True

    def test_02a_instance(self):
        instance_name = None
        for each_item in self.a.Serverless.get_all_for_project(group_id=self.GROUP_ID):
            instance_name = each_item.name
            break
        instance = self.a.Serverless.instance(instance_name=instance_name)
        print(f"Found {instance.name}")
        self.assertIsInstance(instance, ServerlessInstance)

    test_02a_instance.basic = True

    def test_02b_instance_fail_no_group(self):
        instance_name = None
        for each_item in self.a.Serverless.get_all_for_project(group_id=self.GROUP_ID):
            instance_name = each_item.name
            break
        with self.assertRaises(AttributeError):
            instance = self.a_owner.Serverless.instance(instance_name=instance_name)
            print(f"Found {instance.name}")
            self.assertIsInstance(instance, ServerlessInstance)

    test_02b_instance_fail_no_group.basic = True

    def test_03_count(self):
        current_count = self.a.Serverless.count
        print(f"The number of serverless instances is {current_count}")
        self.assertIsInstance(current_count, int)

    test_03_count.basic = True

    def test_04_count_fail_no_group(self):
        with self.assertRaises(AttributeError):
            current_count = self.a_owner.Serverless.count

    test_04_count_fail_no_group.basic = True

    def test_05_instances(self):
        for each_item in self.a.Serverless.instances:
            print(f"Found instance {each_item.name}")
            self.assertIsInstance(each_item, ServerlessInstance)

    test_05_instances.basic = True

    def test_06_instances_no_group(self):
        with self.assertRaises(AttributeError):
            for each_item in self.a_owner.Serverless.instances:
                print(f"Found instance {each_item.name}")
                self.assertIsInstance(each_item, ServerlessInstance)

    test_06_instances_no_group.basic = True

    def test_07_create_basic(self):
        out = self.a.Serverless.create(self.TEST_SERVERLESS_NAME)
        self.assertEqual(out.group_id, self.a.group)
        self.assertIsInstance(out.backup_options, dict)
        self.assertFalse(out.backup_options.get("serverlessContinuousBackupEnabled"))
        self.assertIsInstance(out.provider_settings, ServerlessInstanceProviderSettings)
        self.assertFalse(out.termination_protection)
        self.assertEqual(out.state_name, StateName.creating)

    test_07_create_basic.basic = True

    def test_08_enable_cont_backup(self):
        instance_name = None
        for each_item in self.a.Serverless.get_all_for_project(group_id=self.GROUP_ID):
            instance_name = each_item.name
            break
        output = self.a.Serverless.update_continuous_backup(instance_name, True)
        pprint(output.dict())
        self.assertIsInstance(output, ServerlessInstance)
        backup_setting = output.backup_options
        self.assertIsInstance(backup_setting, dict)
        self.assertIsInstance(backup_setting.get('serverlessContinuousBackupEnabled'), bool)
        # self.assertEqual(backup_setting.get('serverlessContinuousBackupEnabled'), True)
        # Can not really test if this change has been made since the snapshot has to be created before the change is
        # Shown. So we will check that status is updating?
        self.assertIn(output.state_name, [StateName.updating, StateName.creating])
    test_08_enable_cont_backup.basic = True

    def test_09_enable_termination_protection(self):
        instance_name = None
        for each_item in self.a.Serverless.get_all_for_project(group_id=self.GROUP_ID):
            instance_name = each_item.name
            break
        output = self.a.Serverless.update_termination_protection(instance_name, True)
        pprint(output.dict())
        self.assertIsInstance(output, ServerlessInstance)
        self.assertIsInstance(output.termination_protection, bool)
        self.assertEqual(output.termination_protection, True)

    test_09_enable_termination_protection.basic = True

    def test_09a_tp_enable(self):
        instance_name = None
        for each_item in self.a.Serverless.get_all_for_project(group_id=self.GROUP_ID):
            instance_name = each_item.name
            break
        output = self.a.Serverless.termination_protection_enable(name=instance_name)
        pprint(output.dict())

    def test_09b_cps_enable(self):
        instance_name = None
        for each_item in self.a.Serverless.get_all_for_project(group_id=self.GROUP_ID):
            instance_name = each_item.name
            break
        output = self.a.Serverless.continuous_backup_enable(name=instance_name)
        pprint(output.dict())

    def test_10_delete_basic(self):
        out = self.a.Serverless.remove_one(self.TEST_SERVERLESS_NAME)
        pprint(out)

    test_10_delete_basic.basic = True
