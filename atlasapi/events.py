# Copyright (c) 2019 Matthew G. Monteleone
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from isodate import Duration, duration_isoformat
from typing import Iterator, Tuple, NewType, List, Optional, Union
from dateutil.parser import parse
import logging
from datetime import datetime
from enum import Enum
from .atlas_types import OptionalFloat
import ipaddress
from copy import copy

logger = logging.getLogger(name='Atlas_events')


class AtlasEventTypes(Enum):
    PEER_CREATED = "Peer Created"
    PEER_DELETED = "Peer Deleted"
    PEER_UPDATED = "Peer Updated"
    GCP_PEER_CREATED = "Gcp Peer Created"
    GCP_PEER_DELETED = "Gcp Peer Deleted"
    GCP_PEER_UPDATED = "Gcp Peer Updated"
    GCP_PEER_ACTIVE = "Gcp Peer Active"
    GCP_PEER_INACTIVE = "Gcp Peer Inactive"
    AZURE_PEER_CREATED = "Azure Peer Created"
    AZURE_PEER_UPDATED = "Azure Peer Updated"
    AZURE_PEER_ACTIVE = "Azure Peer Active"
    AZURE_PEER_DELETED = "Azure Peer Deleted"
    NEW_AGENT = "New Agent"
    MONITORING_AGENT_UP = "Monitoring Agent Up"
    MONITORING_AGENT_DOWN = "Monitoring Agent Down"
    BACKUP_AGENT_UP = "Backup Agent Up"
    BACKUP_AGENT_DOWN = "Backup Agent Down"
    AUTOMATION_AGENT_UP = "Automation Agent Up"
    AUTOMATION_AGENT_DOWN = "Automation Agent Down"
    NDS_PROXY_UP = "Nds Proxy Up"
    NDS_PROXY_DOWN = "Nds Proxy Down"
    MONITORING_AGENT_VERSION_CURRENT = "Monitoring Agent Version Current"
    MONITORING_AGENT_VERSION_BEHIND = "Monitoring Agent Version Behind"
    BACKUP_AGENT_VERSION_CURRENT = "Backup Agent Version Current"
    BACKUP_AGENT_VERSION_BEHIND = "Backup Agent Version Behind"
    BACKUP_AGENT_CONF_CALL_OK = "Backup Agent Conf Call Ok"
    BACKUP_AGENT_CONF_CALL_FAILURE = "Backup Agent Conf Call Failure"
    ALERT_ACKNOWLEDGED_AUDIT = "Alert Acknowledged Audit"
    ALERT_UNACKNOWLEDGED_AUDIT = "Alert Unacknowledged Audit"
    ALERT_CONFIG_DISABLED_AUDIT = "Alert Config Disabled Audit"
    ALERT_CONFIG_ENABLED_AUDIT = "Alert Config Enabled Audit"
    ALERT_CONFIG_ADDED_AUDIT = "Alert Config Added Audit"
    ALERT_CONFIG_DELETED_AUDIT = "Alert Config Deleted Audit"
    ALERT_CONFIG_CHANGED_AUDIT = "Alert Config Changed Audit"
    AUTOMATION_CONFIG_PUBLISHED_AUDIT = "Automation Config Published Audit"
    OPLOG_CURRENT = "Oplog Current"
    OPLOG_BEHIND = "Oplog Behind"
    RESYNC_PERFORMED = "Resync Performed"
    RESYNC_REQUIRED = "Resync Required"
    BACKUP_RECOVERED = "Backup Recovered"
    BACKUP_IN_UNEXPECTED_STATE = "Backup In Unexpected State"
    BACKUP_TOO_MANY_RETRIES = "Backup Too Many Retries"
    BLOCKSTORE_JOB_RECOVERED = "Blockstore Job Recovered"
    BLOCKSTORE_JOB_TOO_MANY_RETRIES = "Blockstore Job Too Many Retries"
    NO_RS_BIND_ERROR = "No Rs Bind Error"
    RS_BIND_ERROR = "Rs Bind Error"
    TIMELY_SNAPSHOT = "Timely Snapshot"
    LATE_SNAPSHOT = "Late Snapshot"
    GOOD_CLUSTERSHOT = "Good Clustershot"
    BAD_CLUSTERSHOTS = "Bad Clustershots"
    SYNC_SLICE_PROGRESSED = "Sync Slice Progressed"
    SYNC_SLICE_HAS_NOT_PROGRESSED = "Sync Slice Has Not Progressed"
    BACKUP_JOB_NOT_BUSY = "Backup Job Not Busy"
    BACKUP_JOB_TOO_BUSY = "Backup Job Too Busy"
    CONSISTENT_BACKUP_CONFIGURATION = "Consistent Backup Configuration"
    INCONSISTENT_BACKUP_CONFIGURATION = "Inconsistent Backup Configuration"
    DAEMON_AVAILABLE_FOR_QUERYABLE_RESTORE_JOB = "Daemon Available For Queryable Restore Job"
    NO_DAEMON_AVAILABLE_FOR_QUERYABLE_RESTORE_JOB = "No Daemon Available For Queryable Restore Job"
    INITIAL_SYNC_STARTED_AUDIT = "Initial Sync Started Audit"
    INITIAL_SYNC_FINISHED_AUDIT = "Initial Sync Finished Audit"
    RS_STATE_CHANGED_AUDIT = "Rs State Changed Audit"
    CLUSTER_STATE_CHANGED_AUDIT = "Cluster State Changed Audit"
    RESTORE_REQUESTED_AUDIT = "Restore Requested Audit"
    INTERNAL_DIAGNOSTIC_RESTORE_REQUESTED_AUDIT = "Internal Diagnostic Restore Requested Audit"
    SYNC_REQUIRED_AUDIT = "Sync Required Audit"
    SYNC_PENDING_AUDIT = "Sync Pending Audit"
    CLUSTERSHOT_DELETED_AUDIT = "Clustershot Deleted Audit"
    SNAPSHOT_DELETED_AUDIT = "Snapshot Deleted Audit"
    RS_CREDENTIAL_UPDATED_AUDIT = "Rs Credential Updated Audit"
    CLUSTER_CREDENTIAL_UPDATED_AUDIT = "Cluster Credential Updated Audit"
    RS_BLACKLIST_UPDATED_AUDIT = "Rs Blacklist Updated Audit"
    CLUSTER_BLACKLIST_UPDATED_AUDIT = "Cluster Blacklist Updated Audit"
    RS_SNAPSHOT_SCHEDULE_UPDATED_AUDIT = "Rs Snapshot Schedule Updated Audit"
    CLUSTER_SNAPSHOT_SCHEDULE_UPDATED_AUDIT = "Cluster Snapshot Schedule Updated Audit"
    CLUSTER_CHECKPOINT_UPDATED_AUDIT = "Cluster Checkpoint Updated Audit"
    RS_STORAGE_ENGINE_UPDATED_AUDIT = "Rs Storage Engine Updated Audit"
    CLUSTER_STORAGE_ENGINE_UPDATED_AUDIT = "Cluster Storage Engine Updated Audit"
    RS_ROTATE_MASTER_KEY_AUDIT = "Rs Rotate Master Key Audit"
    SNAPSHOT_EXPIRY_UPDATED_AUDIT = "Snapshot Expiry Updated Audit"
    CLUSTERSHOT_EXPIRY_UPDATED_AUDIT = "Clustershot Expiry Updated Audit"
    CPS_RESTORE_REQUESTED_AUDIT = "Cps Restore Requested Audit"
    CPS_SNAPSHOT_SCHEDULE_UPDATED_AUDIT = "Cps Snapshot Schedule Updated Audit"
    CPS_SNAPSHOT_DELETED_AUDIT = "Cps Snapshot Deleted Audit"
    BI_CONNECTOR_DOWN = "Bi Connector Down"
    BI_CONNECTOR_UP = "Bi Connector Up"
    CHARGE_SUCCEEDED = "Charge Succeeded"
    CHARGE_FAILED = "Charge Failed"
    CHECK_PAYMENT_RECEIVED = "Check Payment Received"
    WIRE_TRANSFER_PAYMENT_RECEIVED = "Wire Transfer Payment Received"
    INVOICE_CLOSED = "Invoice Closed"
    CREDIT_CARD_CURRENT = "Credit Card Current"
    CREDIT_CARD_ABOUT_TO_EXPIRE = "Credit Card About To Expire"
    NO_STALE_PENDING_INVOICES = "No Stale Pending Invoices"
    STALE_PENDING_INVOICES = "Stale Pending Invoices"
    INVOICE_BILLED_EQUALS_LINE_ITEMS_TOTAL = "Invoice Billed Equals Line Items Total"
    INVOICE_BILLED_DOES_NOT_EQUAL_LINE_ITEMS_TOTAL = "Invoice Billed Does Not Equal Line Items Total"
    ONE_PENDING_INVOICE = "One Pending Invoice"
    TOO_MANY_PENDING_INVOICES = "Too Many Pending Invoices"
    PENDING_INVOICE_UNDER_THRESHOLD = "Pending Invoice Under Threshold"
    PENDING_INVOICE_OVER_THRESHOLD = "Pending Invoice Over Threshold"
    DAILY_BILL_UNDER_THRESHOLD = "Daily Bill Under Threshold"
    DAILY_BILL_OVER_THRESHOLD = "Daily Bill Over Threshold"
    PAYMENT_METHOD_ADDED = "Payment Method Added"
    MISSING_PAYMENT_METHOD = "Missing Payment Method"
    PREPAID_PLAN_NOT_MISSING_SKU = "Prepaid Plan Not Missing Sku"
    PREPAID_PLAN_MISSING_SKU = "Prepaid Plan Missing Sku"
    PREPAID_PLAN_ACTIVATED = "Prepaid Plan Activated"
    NO_NONZERO_PENDING_REFUNDS = "No Nonzero Pending Refunds"
    NONZERO_PENDING_REFUNDS = "Nonzero Pending Refunds"
    NO_DUPLICATE_SUBSCRIPTION_USAGE = "No Duplicate Subscription Usage"
    DUPLICATE_SUBSCRIPTION_USAGE = "Duplicate Subscription Usage"
    INVOICE_BILLED_EQUALS_PAID = "Invoice Billed Equals Paid"
    INVOICE_BILLED_DOES_NOT_EQUAL_PAID = "Invoice Billed Does Not Equal Paid"
    BILLABLE_HOSTS_INCREASED = "Billable Hosts Increased"
    ONE_INVOICE_FOR_MONTH = "One Invoice For Month"
    MULTIPLE_INVOICES_FOR_MONTH = "Multiple Invoices For Month"
    PAYMENT_METHODS_REMOVED = "Payment Methods Removed"
    DISCOUNT_APPLIED = "Discount Applied"
    CREDIT_ISSUED = "Credit Issued"
    PROMO_CODE_APPLIED = "Promo Code Applied"
    REFUND_ISSUED = "Refund Issued"
    PAYMENT_FORGIVEN = "Payment Forgiven"
    ACCOUNT_UPGRADED = "Account Upgraded"
    ACCOUNT_DOWNGRADED = "Account Downgraded"
    SUPPORT_PLAN_ACTIVATED = "Support Plan Activated"
    SUPPORT_PLAN_CANCELLED = "Support Plan Cancelled"
    SUPPORT_PLAN_CANCELLATION_SCHEDULED = "Support Plan Cancellation Scheduled"
    ACCOUNT_MODIFIED = "Account Modified"
    INVOICE_ADDRESS_ADDED = "Invoice Address Added"
    INVOICE_ADDRESS_CHANGED = "Invoice Address Changed"
    CLUSTER_MONGOS_IS_PRESENT = "Cluster Mongos Is Present"
    CLUSTER_MONGOS_IS_MISSING = "Cluster Mongos Is Missing"
    SHARD_ADDED = "Shard Added"
    SHARD_REMOVED = "Shard Removed"
    DATA_EXPLORER = "Data Explorer"
    DATA_EXPLORER_CRUD = "Data Explorer Crud"
    AWS_ENCRYPTION_KEY_ROTATED = "Aws Encryption Key Rotated"
    AWS_ENCRYPTION_KEY_NEEDS_ROTATION = "Aws Encryption Key Needs Rotation"
    AZURE_ENCRYPTION_KEY_ROTATED = "Azure Encryption Key Rotated"
    AZURE_ENCRYPTION_KEY_NEEDS_ROTATION = "Azure Encryption Key Needs Rotation"
    GCP_ENCRYPTION_KEY_ROTATED = "Gcp Encryption Key Rotated"
    GCP_ENCRYPTION_KEY_NEEDS_ROTATION = "Gcp Encryption Key Needs Rotation"
    CREDIT_CARD_ADDED = "Credit Card Added"
    CREDIT_CARD_UPDATED = "Credit Card Updated"
    GROUP_DELETED = "Group Deleted"
    GROUP_CREATED = "Group Created"
    GROUP_MOVED = "Group Moved"
    GROUP_TEMPORARILY_ACTIVATED = "Group Temporarily Activated"
    GROUP_ACTIVATED = "Group Activated"
    GROUP_LOCKED = "Group Locked"
    GROUP_SUSPENDED = "Group Suspended"
    GROUP_FLUSHED = "Group Flushed"
    GROUP_NAME_CHANGED = "Group Name Changed"
    GROUP_TAGS_CHANGED = "Group Tags Changed"
    FLUSHED = "Flushed"
    ACTIVATED = "Activated"
    ACCOUNT_CLOSED = "Account Closed"
    COMPANY_NAME_OFAC_HIT = "Company Name Ofac Hit"
    GROUP_UNEMBARGOED = "Group Unembargoed"
    AGENT_API_KEY_CREATED = "Agent Api Key Created"
    AGENT_API_KEY_DELETED = "Agent Api Key Deleted"
    PAID_IN_FULL = "Paid In Full"
    DELINQUENT = "Delinquent"
    NO_USERS_AWAITING_APPROVAL = "No Users Awaiting Approval"
    USERS_AWAITING_APPROVAL = "Users Awaiting Approval"
    ALL_USERS_HAVE_MULTI_FACTOR_AUTH = "All Users Have Multi Factor Auth"
    USERS_WITHOUT_MULTI_FACTOR_AUTH = "Users Without Multi Factor Auth"
    NEW_HOST = "New Host"
    HOST_RESTARTED = "Host Restarted"
    HOST_ROLLBACK = "Host Rollback"
    HOST_UPGRADED = "Host Upgraded"
    HOST_DOWNGRADED = "Host Downgraded"
    HOST_VERSION_CHANGED = "Host Version Changed"
    HOST_NOW_PRIMARY = "Host Now Primary"
    HOST_NOW_SECONDARY = "Host Now Secondary"
    HOST_NOW_STANDALONE = "Host Now Standalone"
    HOST_UP = "Host Up"
    HOST_DOWN = "Host Down"
    HOST_RECOVERED = "Host Recovered"
    HOST_RECOVERING = "Host Recovering"
    HOST_VERSION_CURRENT = "Host Version Current"
    HOST_VERSION_BEHIND = "Host Version Behind"
    HOST_SSL_CERTIFICATE_CURRENT = "Host Ssl Certificate Current"
    HOST_SSL_CERTIFICATE_STALE = "Host Ssl Certificate Stale"
    INSIDE_METRIC_THRESHOLD = "Inside Metric Threshold"
    OUTSIDE_METRIC_THRESHOLD = "Outside Metric Threshold"
    ANOMALOUS_VALUE_DETECTED = "Anomalous Value Detected"
    VALUE_NO_LONGER_ANOMALOUS = "Value No Longer Anomalous"
    HOST_LOCKED_DOWN = "Host Locked Down"
    HOST_EXPOSED = "Host Exposed"
    DELETE_HOST_AUDIT = "Delete Host Audit"
    REACTIVATE_HOST_AUDIT = "Reactivate Host Audit"
    DEACTIVATE_HOST_AUDIT = "Deactivate Host Audit"
    ADD_HOST_AUDIT = "Add Host Audit"
    SSH_KEY_NDS_HOST_ACCESS_REQUESTED = "Ssh Key Nds Host Access Requested"
    SSH_KEY_NDS_HOST_ACCESS_ATTEMPT = "Ssh Key Nds Host Access Attempt"
    SSH_KEY_NDS_HOST_ACCESS_GRANTED = "Ssh Key Nds Host Access Granted"
    NDS_HOST_LOGS_DOWNLOADED = "Nds Host Logs Downloaded"
    UNDELETE_HOST_AUDIT = "Undelete Host Audit"
    HIDE_HOST_AUDIT = "Hide Host Audit"
    HIDE_AND_DISABLE_HOST_AUDIT = "Hide And Disable Host Audit"
    DISABLE_HOST_AUDIT = "Disable Host Audit"
    PAUSE_HOST_AUDIT = "Pause Host Audit"
    RESUME_HOST_AUDIT = "Resume Host Audit"
    ADD_HOST_TO_REPLICA_SET_AUDIT = "Add Host To Replica Set Audit"
    REMOVE_HOST_FROM_REPLICA_SET_AUDIT = "Remove Host From Replica Set Audit"
    DB_PROFILER_ENABLE_AUDIT = "Db Profiler Enable Audit"
    DB_PROFILER_DISABLE_AUDIT = "Db Profiler Disable Audit"
    HOST_IP_CHANGED_AUDIT = "Host Ip Changed Audit"
    AUTO_CREATED_INDEX_AUDIT = "Auto Created Index Audit"
    ATTEMPT_KILLOP_AUDIT = "Attempt Killop Audit"
    ATTEMPT_KILLSESSION_AUDIT = "Attempt Killsession Audit"
    LOG_COLLECTION_REQUESTED = "Log Collection Requested"
    LOG_DOWNLOAD_STARTED = "Log Download Started"
    MAINTENANCE_WINDOW_ADDED_AUDIT = "Maintenance Window Added Audit"
    MAINTENANCE_WINDOW_CHANGED_AUDIT = "Maintenance Window Changed Audit"
    MAINTENANCE_WINDOW_DELETED_AUDIT = "Maintenance Window Deleted Audit"
    CLUSTER_CREATED = "Cluster Created"
    CLUSTER_READY = "Cluster Ready"
    CLUSTER_UPDATE_SUBMITTED = "Cluster Update Submitted"
    CLUSTER_UPDATE_STARTED = "Cluster Update Started"
    CLUSTER_UPDATE_COMPLETED = "Cluster Update Completed"
    CLUSTER_PROCESS_ARGS_UPDATE_SUBMITTED = "Cluster Process Args Update Submitted"
    CLUSTER_DELETE_SUBMITTED = "Cluster Delete Submitted"
    CLUSTER_DELETED = "Cluster Deleted"
    CLUSTER_IMPORT_STARTED = "Cluster Import Started"
    CLUSTER_IMPORT_ACKNOWLEDGED = "Cluster Import Acknowledged"
    CLUSTER_IMPORT_CANCELLED = "Cluster Import Cancelled"
    CLUSTER_IMPORT_EXTENDED = "Cluster Import Extended"
    CLUSTER_IMPORT_CUTOVER = "Cluster Import Cutover"
    CLUSTER_IMPORT_VALIDATION_SUCCESS = "Cluster Import Validation Success"
    CLUSTER_IMPORT_VALIDATION_FAIL = "Cluster Import Validation Fail"
    CLUSTER_IMPORT_RESTART_REQUESTED = "Cluster Import Restart Requested"
    CLUSTER_VERSION_FIXED = "Cluster Version Fixed"
    CLUSTER_VERSION_UNFIXED = "Cluster Version Unfixed"
    CLUSTER_OPLOG_RESIZED = "Cluster Oplog Resized"
    CLUSTER_INSTANCE_RESTARTED = "Cluster Instance Restarted"
    CLUSTER_INSTANCE_REPLACED = "Cluster Instance Replaced"
    CLUSTER_INSTANCE_STOP_START = "Cluster Instance Stop Start"
    MONGODB_USER_ADDED = "Mongodb User Added"
    MONGODB_USER_DELETED = "Mongodb User Deleted"
    MONGODB_USER_UPDATED = "Mongodb User Updated"
    MONGODB_ROLE_ADDED = "Mongodb Role Added"
    MONGODB_ROLE_UPDATED = "Mongodb Role Updated"
    MONGODB_ROLE_DELETED = "Mongodb Role Deleted"
    NETWORK_PERMISSION_ENTRY_ADDED = "Network Permission Entry Added"
    NETWORK_PERMISSION_ENTRY_REMOVED = "Network Permission Entry Removed"
    NETWORK_PERMISSION_ENTRY_UPDATED = "Network Permission Entry Updated"
    PLANNING_FAILURE = "Planning Failure"
    PLAN_FAILURE = "Plan Failure"
    PLAN_ABANDONED = "Plan Abandoned"
    MOVE_SKIPPED = "Move Skipped"
    PROXY_RESTARTED = "Proxy Restarted"
    SCHEDULED_MAINTENANCE = "Scheduled Maintenance"
    PROJECT_SCHEDULED_MAINTENANCE = "Project Scheduled Maintenance"
    OS_MAINTENANCE = "Os Maintenance"
    ATLAS_MAINTENANCE_WINDOW_ADDED = "Atlas Maintenance Window Added"
    ATLAS_MAINTENANCE_WINDOW_MODIFIED = "Atlas Maintenance Window Modified"
    ATLAS_MAINTENANCE_WINDOW_REMOVED = "Atlas Maintenance Window Removed"
    ATLAS_MAINTENANCE_DEFERRED = "Atlas Maintenance Deferred"
    ATLAS_MAINTENANCE_START_ASAP = "Atlas Maintenance Start Asap"
    FREE_UPGRADE_STARTED = "Free Upgrade Started"
    TEST_FAILOVER_REQUESTED = "Test Failover Requested"
    USER_SECURITY_SETTINGS_UPDATED = "User Security Settings Updated"
    AUDIT_LOG_CONFIGURATION_UPDATED = "Audit Log Configuration Updated"
    ENCRYPTION_AT_REST_CONFIGURATION_UPDATED = "Encryption At Rest Configuration Updated"
    ENCRYPTION_AT_REST_CONFIGURATION_VALIDATION_FAILED = "Encryption At Rest Configuration Validation Failed"
    AGENT_VERSION_FIXED = "Agent Version Fixed"
    AGENT_VERSION_UNFIXED = "Agent Version Unfixed"
    CLUSTER_INSTANCE_CONFIG_UPDATED = "Cluster Instance Config Updated"
    CLUSTER_INSTANCE_SSL_ROTATED = "Cluster Instance Ssl Rotated"
    NDS_SET_IMAGE_OVERRIDES = "Nds Set Image Overrides"
    RESTRICTED_EMPLOYEE_ACCESS_BYPASS = "Restricted Employee Access Bypass"
    QUERY_ENGINE_TENANT_CREATED = "Query Engine Tenant Created"
    ORG_CREDIT_CARD_ADDED = "Org Credit Card Added"
    ORG_CREDIT_CARD_UPDATED = "Org Credit Card Updated"
    ORG_CREDIT_CARD_CURRENT = "Org Credit Card Current"
    ORG_CREDIT_CARD_ABOUT_TO_EXPIRE = "Org Credit Card About To Expire"
    ORG_ACTIVATED = "Org Activated"
    ORG_TEMPORARILY_ACTIVATED = "Org Temporarily Activated"
    ORG_IP_WHITELIST_DELETED = "Org Ip Whitelist Deleted"
    ORG_CLUSTERS_DELETED = "Org Clusters Deleted"
    ORG_SUSPENDED = "Org Suspended"
    ORG_ADMIN_SUSPENDED = "Org Admin Suspended"
    ORG_LOCKED = "Org Locked"
    ORG_COMPANY_NAME_OFAC_HIT = "Org Company Name Ofac Hit"
    ORG_EMBARGO_CONFIRMED = "Org Embargo Confirmed"
    ORG_UNEMBARGOED = "Org Unembargoed"
    ORG_CREATED = "Org Created"
    ORG_DELETED = "Org Deleted"
    ORG_RENAMED = "Org Renamed"
    ALL_ORG_USERS_HAVE_MFA = "All Org Users Have Mfa"
    ORG_USERS_WITHOUT_MFA = "Org Users Without Mfa"
    ORG_INVOICE_UNDER_THRESHOLD = "Org Invoice Under Threshold"
    ORG_INVOICE_OVER_THRESHOLD = "Org Invoice Over Threshold"
    ORG_DAILY_BILL_UNDER_THRESHOLD = "Org Daily Bill Under Threshold"
    ORG_DAILY_BILL_OVER_THRESHOLD = "Org Daily Bill Over Threshold"
    ORG_GROUP_CHARGES_UNDER_THRESHOLD = "Org Group Charges Under Threshold"
    ORG_GROUP_CHARGES_OVER_THRESHOLD = "Org Group Charges Over Threshold"
    ORG_TWO_FACTOR_AUTH_REQUIRED = "Org Two Factor Auth Required"
    ORG_TWO_FACTOR_AUTH_OPTIONAL = "Org Two Factor Auth Optional"
    ORG_PUBLIC_API_WHITELIST_REQUIRED = "Org Public Api Whitelist Required"
    ORG_PUBLIC_API_WHITELIST_NOT_REQUIRED = "Org Public Api Whitelist Not Required"
    ORG_EMPLOYEE_ACCESS_RESTRICTED = "Org Employee Access Restricted"
    ORG_EMPLOYEE_ACCESS_UNRESTRICTED = "Org Employee Access Unrestricted"
    ORG_SFDC_ACCOUNT_ID_CHANGED = "Org Sfdc Account Id Changed"
    ORG_CONNECTED_TO_MLAB = "Org Connected To Mlab"
    ORG_DISCONNECTED_FROM_MLAB = "Org Disconnected From Mlab"
    MONITORING_AGENT_LOGS = "Monitoring Agent Logs"
    MONITORING_AGENT_LOGS_CSV_DOWNLOAD = "Monitoring Agent Logs Csv Download"
    AUTOMATION_AGENT_LOGS = "Automation Agent Logs"
    AUTOMATION_AGENT_LOGS_CSV_DOWNLOAD = "Automation Agent Logs Csv Download"
    BACKUP_AGENT_LOGS = "Backup Agent Logs"
    BACKUP_AGENT_LOGS_CSV_DOWNLOAD = "Backup Agent Logs Csv Download"
    MONITORING_MONGOD_LOGS = "Monitoring Mongod Logs"
    VIEWED_MONITORING_HOST_SPECIFIC_MONGOD_LOGS = "Viewed Monitoring Host Specific Mongod Logs"
    DOWNLOADED_MONITORING_HOST_SPECIFIC_MONGOD_LOGS = "Downloaded Monitoring Host Specific Mongod Logs"
    DOWNLOADED_MONITORING_GROUP_MONGOD_LOGS = "Downloaded Monitoring Group Mongod Logs"
    VIEWED_AUTOMATION_MONGOD_LOGS = "Viewed Automation Mongod Logs"
    BACKUP_MONGOD_LOGS = "Backup Mongod Logs"
    ATLAS_PROXY_LOGS = "Atlas Proxy Logs"
    ATLAS_MONGOD_LOGS = "Atlas Mongod Logs"
    ATLAS_MONGOS_LOGS = "Atlas Mongos Logs"
    ATLAS_MONGOSQLD_LOGS = "Atlas Mongosqld Logs"
    ATLAS_MONGOMIRROR_LOGS = "Atlas Mongomirror Logs"
    ATLAS_MONGODUMP_LOGS = "Atlas Mongodump Logs"
    ATLAS_MONGORESTORE_LOGS = "Atlas Mongorestore Logs"
    VISUAL_PROFILER = "Visual Profiler"
    REAL_TIME_PERFORMANCE_PANEL = "Real Time Performance Panel"
    PERFORMANCE_ADVISOR = "Performance Advisor"
    TOGGLEABLE_FEATURE_FLAG = "Toggleable Feature Flag"
    MONITORING_DAILY_PING = "Monitoring Daily Ping"
    MONITORING_LATEST_HOST_SPECIFIC_PING = "Monitoring Latest Host Specific Ping"
    MONITORING_GROUP_PING = "Monitoring Group Ping"
    PUBLIC_API_LATEST_MONITORING_GROUP_PING = "Public Api Latest Monitoring Group Ping"
    PUBLIC_API_LATEST_MONITORING_HOST_SPECIFIC_PING = "Public Api Latest Monitoring Host Specific Ping"
    MEMBER_ADDED = "Member Added"
    MEMBER_REMOVED = "Member Removed"
    CONFIGURATION_CHANGED = "Configuration Changed"
    ENOUGH_HEALTHY_MEMBERS = "Enough Healthy Members"
    TOO_FEW_HEALTHY_MEMBERS = "Too Few Healthy Members"
    TOO_MANY_UNHEALTHY_MEMBERS = "Too Many Unhealthy Members"
    TOO_MANY_ELECTIONS = "Too Many Elections"
    REPLICATION_OPLOG_WINDOW_RUNNING_OUT = "Replication Oplog Window Running Out"
    REPLICATION_OPLOG_WINDOW_HEALTHY = "Replication Oplog Window Healthy"
    REPLICATION_OPLOG_WINDOW_TREND_HEALTHY = "Replication Oplog Window Trend Healthy"
    PRIMARY_ELECTED = "Primary Elected"
    ONE_PRIMARY = "One Primary"
    MULTIPLE_PRIMARIES = "Multiple Primaries"
    NO_PRIMARY = "No Primary"
    REQUEST_INCOMPLETE = "Request Incomplete"
    CASE_CREATED = "Case Created"
    AWS_AVAILABILITY_ZONE_OK = "Aws Availability Zone Ok"
    AWS_AVAILABILITY_ZONE_DOWN = "Aws Availability Zone Down"
    GROUP_ALERT_PROCESSING_ENABLED = "Group Alert Processing Enabled"
    GROUP_ALERT_PROCESSING_DISABLED = "Group Alert Processing Disabled"
    AZURE_REGION_OK = "Azure Region Ok"
    AZURE_REGION_DOWN = "Azure Region Down"
    SUFFICIENT_HEAD_FREE_SPACE = "Sufficient Head Free Space"
    LOW_HEAD_FREE_SPACE = "Low Head Free Space"
    LOW_HEAD_FREE_SPACE_PERCENT = "Low Head Free Space Percent"
    DAEMON_UP = "Daemon Up"
    DAEMON_DOWN = "Daemon Down"
    OPLOG_TTL_RESIZE = "Oplog Ttl Resize"
    THEFT_FAILED = "Theft Failed"
    GROUP_CLOSED = "Group Closed"
    GROUP_STUCK_IN_CLOSING = "Group Stuck In Closing"
    BALANCER_OFF = "Balancer Off"
    BALANCER_ON = "Balancer On"
    INSIDE_SPACE_USED_THRESHOLD = "Inside Space Used Threshold"
    OUTSIDE_SPACE_USED_THRESHOLD = "Outside Space Used Threshold"
    SNAPSHOT_STORE_DELETED = "Snapshot Store Deleted"
    SNAPSHOT_STORE_CONFIG_CHANGE = "Snapshot Store Config Change"
    OPLOG_STORE_DELETED = "Oplog Store Deleted"
    OPLOG_STORE_CONFIG_CHANGE = "Oplog Store Config Change"
    SYNC_STORE_DELETED = "Sync Store Deleted"
    SYNC_STORE_CONFIG_CHANGE = "Sync Store Config Change"
    DAEMON_DELETED = "Daemon Deleted"
    DAEMON_CONFIG_CHANGE = "Daemon Config Change"
    GROUP_CONFIG_CHANGE = "Group Config Change"
    PROVISIONING_CHANGE = "Provisioning Change"
    JOB_CHANGE = "Job Change"
    BREAK_JOB = "Break Job"
    BULK_HEAD_MOVE = "Bulk Head Move"
    SCHEDULE_GROOM = "Schedule Groom"
    LOG_LEVEL_CHANGE = "Log Level Change"
    CRON_JOB_COMPLETED = "Cron Job Completed"
    CRON_JOB_FAILED = "Cron Job Failed"
    CRON_JOB_ENABLED = "Cron Job Enabled"
    CRON_JOB_DISABLED = "Cron Job Disabled"
    BACKING_DATABASE_PROCESS_UP = "Backing Database Process Up"
    BACKING_DATABASE_PROCESS_DOWN = "Backing Database Process Down"
    BACKING_DATABASE_PROCESS_NO_STARTUP_WARNINGS = "Backing Database Process No Startup Warnings"
    BACKING_DATABASE_PROCESS_STARTUP_WARNINGS = "Backing Database Process Startup Warnings"
    GCP_ZONE_OK = "Gcp Zone Ok"
    GCP_ZONE_DOWN = "Gcp Zone Down"
    LOG_DEBUG_OVERRIDE_ACTIVE = "Log Debug Override Active"
    MTM_CAPACITY_OK = "Mtm Capacity Ok"
    MTM_CAPACITY_LOW = "Mtm Capacity Low"
    TEAM_CREATED = "Team Created"
    TEAM_DELETED = "Team Deleted"
    TEAM_UPDATED = "Team Updated"
    TEAM_NAME_CHANGED = "Team Name Changed"
    USER_ADDED_TO_TEAM = "User Added To Team"
    TEAM_ADDED_TO_GROUP = "Team Added To Group"
    TEAM_REMOVED_FROM_GROUP = "Team Removed From Group"
    TEAM_ROLES_MODIFIED = "Team Roles Modified"
    MULTI_FACTOR_AUTH_RESET_EMAIL_SENT_AUDIT = "Multi Factor Auth Reset Email Sent Audit"
    MULTI_FACTOR_AUTH_RESET_AUDIT = "Multi Factor Auth Reset Audit"
    MULTI_FACTOR_AUTH_UPDATED_AUDIT = "Multi Factor Auth Updated Audit"
    JOINED_GROUP = "Joined Group"
    JOINED_ORG = "Joined Org"
    JOINED_TEAM = "Joined Team"
    REMOVED_FROM_GROUP = "Removed From Group"
    INVITED_TO_GROUP = "Invited To Group"
    INVITED_TO_ORG = "Invited To Org"
    REQUESTED_TO_JOIN_GROUP = "Requested To Join Group"
    REMOVED_FROM_ORG = "Removed From Org"
    REMOVED_FROM_TEAM = "Removed From Team"
    PASSWORD_RESET_EMAIL_SENT_AUDIT = "Password Reset Email Sent Audit"
    PASSWORD_RESET_FORM_VIEWED_AUDIT = "Password Reset Form Viewed Audit"
    PASSWORD_RESET_FAILED_AUDIT = "Password Reset Failed Audit"
    PASSWORD_RESET_AUDIT = "Password Reset Audit"
    PASSWORD_UPDATED_AUDIT = "Password Updated Audit"
    PASSWORD_UPDATE_FAILED_AUDIT = "Password Update Failed Audit"
    USER_EMAIL_ADDRESS_CHANGED_AUDIT = "User Email Address Changed Audit"
    USER_FIRST_NAME_LAST_NAME_CHANGED_AUDIT = "User First Name Last Name Changed Audit"
    USER_ROLES_CHANGED_AUDIT = "User Roles Changed Audit"
    SUCCESSFUL_LOGIN_AUDIT = "Successful Login Audit"
    UNSUCCESSFUL_LOGIN_AUDIT = "Unsuccessful Login Audit"
    ACCOUNT_LOCKED_AUDIT = "Account Locked Audit"
    ACCOUNT_UNLOCKED_AUDIT = "Account Unlocked Audit"
    USER_CREATED_AUDIT = "User Created Audit"
    JOIN_GROUP_REQUEST_DENIED_AUDIT = "Join Group Request Denied Audit"
    JOIN_GROUP_REQUEST_APPROVED_AUDIT = "Join Group Request Approved Audit"
    USER_DELETED_AUDIT = "User Deleted Audit"
    USER_HARD_DELETED_AUDIT = "User Hard Deleted Audit"
    USER_RESTORED_AUDIT = "User Restored Audit"
    USER_NAME_OFAC_HIT = "User Name Ofac Hit"
    USER_UNEMBARGOED = "User Unembargoed"
    GROUP_CHARTS_UPGRADED = 'Group Charts Upgraded'
    UNKNOWN = "Unknown or None"


class _AtlasBaseEvent(object):
    def __init__(self, value_dict: dict) -> None:
        self.created_date = None
        try:
            self.created_date = parse(value_dict.get("created", None))
        except ValueError as e:
            logger.warning("Could not parse datetime value for created_date: {}".format(e))
            pass
        self.event_type = AtlasEventTypes[value_dict.get('eventTypeName', 'UNKNOWN')]  # type: AtlasEventTypes
        self.group_id = value_dict.get('groupId', None)  # type: str
        self.id = value_dict.get('id', None)  # type: str
        self.is_global_admin = value_dict.get('isGlobalAdmin', False)  # type: bool
        self.links = value_dict.get('links', None)  # type: list
        self.event_dict = value_dict  # type: dict

    def as_dict(self):
        original_dict = self.__dict__
        return_dict = copy(original_dict)
        del return_dict['event_dict']
        return_dict['created_date'] = datetime.isoformat(self.created_date)
        return_dict['event_type'] = self.event_type.name
        return_dict['event_type_desc'] = self.event_type.value

        if return_dict.get('remote_address'):
            return_dict['remote_address'] = return_dict['remote_address'].__str__()
        return return_dict


class _AtlasUserBaseEvent(_AtlasBaseEvent):
    def __init__(self, value_dict: dict) -> None:
        super().__init__(value_dict)
        self.user_id = value_dict.get('userId', None)  # type: str
        self.username = value_dict.get('username')  # type: str
        try:
            self.remote_address = ipaddress.ip_address(value_dict.get('remoteAddress', None))  # type: ipaddress
        except ValueError:
            logger.info('No IP address found')
            self.remote_address = None


class AtlasEvent(_AtlasBaseEvent):
    def __init__(self, value_dict: dict) -> None:
        super().__init__(value_dict)


class AtlasDataExplorerEvent(_AtlasUserBaseEvent):
    def __init__(self, value_dict: dict) -> None:
        super().__init__(value_dict)
        self.database = value_dict.get('database', None)  # type: str
        self.collection = value_dict.get('collection', None)  # type: str
        self.op_type = value_dict.get('opType', None)  # type: str


class AtlasClusterEvent(_AtlasBaseEvent):
    def __init__(self, value_dict: dict) -> None:
        super().__init__(value_dict)
        self.replica_set_name = value_dict.get('replicaSetName', None)  # type: str
        self.cluster_name = value_dict.get('clusterName', None)  # type: str


class AtlasHostEvent(_AtlasBaseEvent):
    def __init__(self, value_dict: dict) -> None:
        super().__init__(value_dict)
        self.hostname = value_dict.get('hostname', None)  # type: str
        self.port = value_dict.get('port', None)  # type: int
        self.replica_set_name = value_dict.get('replicaSetName', None)  # type: str


class AtlasFeatureEvent(_AtlasUserBaseEvent):
    def __init__(self, value_dict: dict) -> None:
        super().__init__(value_dict)
        self.hostname = value_dict.get('hostname', None)  # type: str
        self.feature_name = value_dict.get('featureName', None)  # type: str


def atlas_event_factory(value_dict: dict) -> Union[
                            AtlasEvent, AtlasDataExplorerEvent, AtlasClusterEvent, AtlasHostEvent, AtlasFeatureEvent]:
    if value_dict.get("featureName", None):
        return AtlasFeatureEvent(value_dict=value_dict)

    elif value_dict.get("hostname", None):
        return AtlasHostEvent(value_dict=value_dict)

    elif value_dict.get("clusterName", None):
        return AtlasClusterEvent(value_dict=value_dict)

    elif value_dict.get("database", None):
        return AtlasDataExplorerEvent(value_dict=value_dict)
    else:
        return AtlasEvent(value_dict=value_dict)


ListOfEvents = NewType('ListOfEvents', List[Union[dict, _AtlasBaseEvent]])
