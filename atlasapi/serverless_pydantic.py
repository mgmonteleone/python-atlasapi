from __future__ import annotations

from datetime import datetime
from enum import Enum
from ipaddress import IPv4Address
from typing import Any, Dict, List, Optional, Union, TypedDict
from uuid import UUID

from pydantic import BaseModel, EmailStr, Extra, Field, confloat, conint, constr


class DeletedReturn(TypedDict):
    deleted: Required[bool]


class ServerlessRegionName(Enum):
    US_EAST_1 = "US_EAST_1"
    US_EAST_2 = "US_EAST_2"
    US_WEST_2 = "US_WEST_2"
    AP_SOUTHEAST_1 = "AP_SOUTHEAST_1"
    AP_SOUTHEAST_2 = "AP_SOUTHEAST_2"
    AP_SOUTHEAST_3 = "AP_SOUTHEAST_3"
    AP_SOUTH_1 = "AP_SOUTH_1"
    EU_WEST_1 = "EU_WEST_1"


class Type(str, Enum):
    """
    MongoDB process type to which your application connects. Use `MONGOD` for replica sets and
    `MONGOS` for sharded clusters.
    """

    mongod = 'MONGOD'
    mongos = 'MONGOS'


class ServerlessProviderName(str, Enum):
    """
    Cloud service provider that serves the requested network peering containers.
    """

    aws = 'AWS'
    gcp = 'GCP'
    azure = 'AZURE'
    tenant = 'TENANT'
    serverless = 'SERVERLESS'


class BackingProviderName(str, Enum):
    """
    Cloud service provider on which MongoDB Cloud provisioned the serverless instance.
    """

    aws = 'AWS'
    azure = 'AZURE'
    gcp = 'GCP'


class StateName(str, Enum):
    """
    Human-readable label that indicates the current operating condition of this cluster.
    """

    creating = 'CREATING'
    deleted = 'DELETED'
    deleting = 'DELETING'
    idle = 'IDLE'
    repairing = 'REPAIRING'
    updating = 'UPDATING'


class EndpointStatus(str, Enum):
    """
    Human-readable label that indicates the current operating status of the private endpoint.
    """

    reservation_requested = 'RESERVATION_REQUESTED'
    reserved = 'RESERVED'
    available = 'AVAILABLE'
    initiating = 'INITIATING'
    deleting = 'DELETING'
    failed = 'FAILED'


class Link(BaseModel):
    href: Optional[str] = Field(
        None,
        description='Uniform Resource Locator (URL) that points another API resource to which this response has some '
                    'relationship. This URL often begins with `https://mms.mongodb.com`.',
        example='https://mms.mongodb.com/api/atlas/v1.0/groups/{groupId}/serverless/{instanceName1}/backup/snapshots',
    )
    rel: Optional[str] = Field(
        None,
        description='Uniform Resource Locator (URL) that defines the semantic relationship between this resource and '
                    'another API resource. This URL often begins with `https://mms.mongodb.com`.',
        example='https://mms.mongodb.com/snapshots',
    )


class LinkAtlas(BaseModel):
    href: Optional[str] = Field(
        None,
        description='Uniform Resource Locator (URL) that points another API resource to which this response has some '
                    'relationship. This URL often begins with `https://mms.mongodb.com`.',
        example='https://mms.mongodb.com/api/atlas/v1.0/groups/{groupId}/serverless/{instanceName1}/backup/snapshots',
    )
    rel: Optional[str] = Field(
        None,
        description='Uniform Resource Locator (URL) that defines the semantic relationship between this resource and '
                    'another API resource. This URL often begins with `https://mms.mongodb.com`.',
        example='https://mms.mongodb.com/snapshots',
    )


class ServerlessAWSTenantEndpointView(BaseModel):
    """
    View for a serverless AWS tenant endpoint.
    """

    _id: Optional[
        constr(regex=r'^([a-f0-9]{24})$', min_length=24, max_length=24)
    ] = Field(
        None,
        description='Unique 24-hexadecimal digit string that identifies the private endpoint.',
        example='76232bec98341ad1155cc244',
    )
    cloud_provider_endpoint_id: Optional[
        constr(
            regex=r'^(vpce-[0-9a-f]{17}|\/subscriptions\/[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}\/resource['
                  r'gG]roups\/private[Ll]ink\/providers\/Microsoft\.Network\/privateEndpoints\/[-\w._()]+)$ '
        )
    ] = Field(
        None,
        alias='cloudProviderEndpointId',
        description="Unique string that identifies the private endpoint's network interface.",
    )
    comment: Optional[constr(max_length=80)] = Field(
        None, description='Human-readable comment associated with the private endpoint.'
    )
    endpoint_service_name: Optional[
        constr(
            regex=r'^com\.amazonaws\.vpce\.[a-z-0-9]+\.vpce-svc-[0-9a-f]{17}|pls_[0-9a-f]{24}$'
        )
    ] = Field(
        None,
        alias='endpointServiceName',
        description='Unique string that identifies the PrivateLink endpoint service. MongoDB Cloud returns null while '
                    'it creates the endpoint service.',
    )
    error_message: Optional[str] = Field(
        None,
        alias='errorMessage',
        description='Human-readable error message that indicates error condition associated with establishing the'
                    ' private endpoint connection.',
    )
    status: Optional[EndpointStatus] = Field(
        None,
        description='Human-readable label that indicates the current operating status of the private endpoint.',
    )


class ServerlessAzureTenantEndpointView(BaseModel):
    """
    View for a serverless Azure tenant endpoint.
    """

    _id: Optional[
        constr(regex=r'^([a-f0-9]{24})$', min_length=24, max_length=24)
    ] = Field(
        None,
        description='Unique 24-hexadecimal digit string that identifies the private endpoint.',
        example='76232bec98341ad1155cc244',
    )
    cloud_provider_endpoint_id: Optional[
        constr(
            regex=r'^(vpce-[0-9a-f]{17}|\/subscriptions\/[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}\/resource['
                  r'gG]roups\/private[Ll]ink\/providers\/Microsoft\.Network\/privateEndpoints\/[-\w._()]+)$ '
        )
    ] = Field(
        None,
        alias='cloudProviderEndpointId',
        description="Unique string that identifies the private endpoint's network interface.",
    )
    comment: Optional[constr(max_length=80)] = Field(
        None, description='Human-readable comment associated with the private endpoint.'
    )
    endpoint_service_name: Optional[
        constr(
            regex=r'^com\.amazonaws\.vpce\.[a-z-0-9]+\.vpce-svc-[0-9a-f]{17}|pls_[0-9a-f]{24}$'
        )
    ] = Field(
        None,
        alias='endpointServiceName',
        description='Unique string that identifies the PrivateLink endpoint service. MongoDB Cloud returns null while '
                    'it creates the endpoint service.',
    )
    error_message: Optional[str] = Field(
        None,
        alias='errorMessage',
        description='Human-readable error message that indicates error condition associated with establishing the '
                    'private endpoint connection.',
    )
    private_endpoint_ip_address: Optional[
        constr(
            regex=r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}',
            min_length=24,
            max_length=24,
        )
    ] = Field(
        None,
        alias='privateEndpointIpAddress',
        description='IPv4 address of the private endpoint in your Azure VNet that someone'
                    ' added to this private endpoint service.',
    )
    private_link_service_resource_id: Optional[
        constr(
            regex=r'^\/subscriptions\/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\/resource['
                  r'gG]roups\/([-\w._()]+)\/providers\/Microsoft\.Network/privateLinkServices\/pls_[0-9a-f]{24} '
        )
    ] = Field(
        None,
        alias='privateLinkServiceResourceId',
        description='Root-relative path that identifies the Azure Private Link Service that MongoDB Cloud manages. '
                    'MongoDB Cloud returns null while it creates the endpoint service.',
    )
    status: Optional[Status16] = Field(
        None,
        description='Human-readable label that indicates the current operating status of the private endpoint.',
    )


class ServerlessInstancePrivateEndpointEndpoint(BaseModel):
    endpoint_id: str = Field(
        ...,
        alias='endpointId',
        description='Unique provider identifier of the private endpoint.\n',
    )
    provider_name: ProviderName = Field(
        ...,
        alias='providerName',
        description='Cloud provider where the private endpoint is deployed.\n',
    )
    region: str = Field(
        ..., description='Region where the private endpoint is deployed.\n'
    )


class ServerlessInstancePrivateEndpoint(BaseModel):
    endpoints: List[ServerlessInstancePrivateEndpointEndpoint] = Field(
        ...,
        description='List that contains the private endpoints through which you connect to'
                    ' MongoDB Cloud when you use **connectionStrings.privateEndpoint[n].srvConnectionString**.',
    )
    srv_connection_string: str = Field(
        ...,
        alias='srvConnectionString',
        description='Private endpoint-aware connection string that uses the `mongodb+srv://` protocol to connect to'
                    ' MongoDB Cloud through a private endpoint. The `mongodb+srv` protocol tells the driver '
                    'to look up the seed list of hosts in the Domain Name System (DNS).',
    )
    type: Type = Field(
        ..., description='MongoDB process type to which your application connects.\n'
    )


class ServerlessInstanceConnectionStrings(BaseModel):
    """
    Collection of Uniform Resource Locators that point to the MongoDB database.
    """

    private_endpoint: Optional[List[ServerlessInstancePrivateEndpoint]] = Field(
        None,
        alias='privateEndpoint',
        description='List of private endpoint connection strings that you can use to connect to this serverless'
                    ' instance through a private endpoint. This parameter returns only if you created a private '
                    'endpoint for this serverless instance and it is AVAILABLE.',
    )
    standard_srv: Optional[str] = Field(
        None,
        alias='standardSrv',
        description='Public connection string that you can use to connect to this serverless instance. This connection '
                    'string uses the `mongodb+srv://` protocol.',
    )


class ServerlessInstanceProviderSettings(BaseModel):
    """
    Group of settings that configure the provisioned MongoDB serverless instance. The options available relate
    to the cloud service provider.
    """

    backing_provider_name: Optional[BackingProviderName] = Field(
        None,
        alias='backingProviderName',
        description='Cloud service provider on which MongoDB Cloud provisioned the serverless instance.',
    )
    provider_name: ServerlessProviderName = Field(
        None,
        alias='providerName',
        description='Human-readable label that identifies the cloud service provider.',
    )
    region_name: Optional[ServerlessRegionName] = Field(
        None,
        alias='regionName',
        description='Human-readable label that identifies the geographic location of your '
                    'MongoDB serverless instance. The region you choose can affect network '
                    'latency for clients accessing your databases. For a complete list of region names,'
                    ' see [AWS](https://docs.atlas.mongodb.com/reference/amazon-aws/#std-label-amazon-aws),'
                    ' [GCP](https://docs.atlas.mongodb.com/reference/google-gcp/), '
                    'and [Azure](https://docs.atlas.mongodb.com/reference/microsoft-azure/).'
                    'An Enum is maintained in this library, which allows only supported regions.'
                    'This Enum is updated over time.',
    )

    class Config:
        use_enum_values = False


class ServerlessInstance(BaseModel):
    connection_strings: Optional[ServerlessInstanceConnectionStrings] = Field(
        None, alias='connectionStrings'
    )
    create_date: Optional[datetime] = Field(
        None,
        alias='createDate',
        description='Date and time when MongoDB Cloud created this serverless instance. MongoDB Cloud represents'
                    ' this timestamp in ISO 8601 format in UTC.',
    )
    group_id: Optional[
        constr(regex=r'^([a-f0-9]{24})$', min_length=24, max_length=24)
    ] = Field(
        None,
        alias='groupId',
        description='Unique 24-hexadecimal character string that identifies the project.',
        example='32b6e34b3d91647abb20e7b8',
    )
    id: Optional[
        constr(regex=r'^([a-f0-9]{24})$', min_length=24, max_length=24)
    ] = Field(
        None,
        description='Unique 24-hexadecimal digit string that identifies the serverless instance.',
        example='e870889e64835532ca903154',
    )
    links: Optional[List[Link]] = Field(
        None,
        description='List of one or more Uniform Resource Locators (URLs) that point to '
                    'API sub-resources, related API resources, or both. RFC 5988 outlines these relationships.',
    )
    mongo_db_version: Optional[constr(regex=r'(\d+\.\d+\.\d+)')] = Field(
        None,
        alias='mongoDBVersion',
        description='Version of MongoDB that the serverless instance runs.',
    )
    name: Optional[
        constr(
            regex=r'^([a-zA-Z0-9]([a-zA-Z0-9-]){0,21}(?<!-)([\w]{0,42}))$',
            min_length=1,
            max_length=64,
        )
    ] = Field(
        None,
        description='Human-readable label that identifies the serverless instance.',
    )
    provider_settings: Optional[ServerlessInstanceProviderSettings] = Field(
        None, alias='providerSettings'
    )
    state_name: Optional[StateName] = Field(
        None,
        alias='stateName',
        description='Human-readable label that indicates the current operating condition of the serverless instance.',
    )
    backup_options: Optional[dict] = Field(
        {"serverlessContinuousBackupEnabled": False},
        alias="serverlessBackupOptions",
        description="Flag that indicates whether the serverless instance uses Serverless Continuous Backup. "
                    "If this parameter is false, the serverless instance uses Basic Backup."
                    "Note: This library sets this to False by default, as a sane (no cost) default."
    )
    termination_protection: Optional[bool] = Field(
        False,
        alias="terminationProtectionEnabled",
        description="Flag that indicates whether termination protection is enabled on the serverless instance. "
                    "If set to true, MongoDB Cloud won't delete the serverless instance. If set to false,"
                    " MongoDB Cloud will delete the serverless instance."
    )

    class Config:
        use_enum_values = False
