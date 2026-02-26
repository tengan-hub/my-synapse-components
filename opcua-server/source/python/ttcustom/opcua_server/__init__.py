from __future__ import annotations

import asyncio
from pathlib import Path
import typing
from asyncua import ua, Server
from asyncua.common.node import Node
from asyncua.server.user_managers import User, UserManager, UserRole
from asyncua.crypto.validator import CertificateValidator, CertificateValidatorOptions, TrustStore
from dataclasses import dataclass
from speedbeesynapse.component.base import DataType, HiveComponentBase, HiveComponentInfo, ErrorType

from ttcustom.opcua_server.certificate import create_cert


PARAMETER_ERROR = ErrorType('PARAMETER ERROR','detail')
ERROR_TYPES = [PARAMETER_ERROR]


class OPCUAVariable:
    def __init__(self, data_name: str, data_type: str, node: Node):
        self.name = data_name
        self.data_type = data_type
        self.node = node

    @classmethod
    async def create(cls, namespace_idx: int, parent_node: Node, column: any):
        node_id = ua.NodeId(f'{column.source_name}:{column.data_name}', namespace_idx, ua.NodeIdType.String)
        variable_node = await parent_node.add_variable(node_id, column.data_name, column.get_latest_value()[1])
        return cls(column.data_name, column.data_type, variable_node)

    async def update_value(self, value: any):
        await self.node.write_value(value)

class OPCUAComponentObject:
    def __init__(self, component_name: str, node: Node):
        self.name: str = component_name
        self.node: Node = node
        self.variables: list[OPCUAVariable] = []

    @classmethod
    async def create(cls, namespace_idx: int, component_name: str, folder: Node) -> OPCUAComponentObject:
        node_id = ua.NodeId(component_name, namespace_idx, ua.NodeIdType.String)
        component_node = await folder.add_object(node_id, component_name)
        return cls(component_name, component_node)

    def get_variable(self, variable_name: str) -> typing.Optional[OPCUAVariable]:
        for variable in self.variables:
            if variable.name == variable_name:
                return variable
        return None

    async def add_variable(self, namespace_idx: int, column: any) -> OPCUAVariable:
        variable = await OPCUAVariable.create(namespace_idx, self.node, column)
        self.variables.append(variable)
        return variable

class OPCUAComponentsFolder:
    def __init__(self, node: Node):
        self.node = node
        self.component_objects: list[OPCUAComponentObject] = []

    @classmethod
    async def create(cls, server: Server, namespace_idx: int) -> OPCUAComponentsFolder:
        components_folder = await server.nodes.objects.add_folder(namespace_idx, "Components")
        return cls(components_folder)

    def get_component_object(self, component_name: str) -> typing.Optional[OPCUAComponentObject]:
        for component_obj in self.component_objects:
            if component_obj.name == component_name:
                return component_obj
        return None
    
    async def add_component_object(self, namespace_idx: int, component_name: str) -> OPCUAComponentObject:
        component_obj = await OPCUAComponentObject.create(namespace_idx, component_name, self.node)
        self.component_objects.append(component_obj)
        return component_obj

class CustomUserManager(UserManager):
    def __init__(self, logger):
        self.users = [
            {"username": "admin", "password": "admin"},
            {"username": "user", "password": "password"},
        ]
        self.log = logger

    def get_user(self, iserver, username=None, password=None, certificate=None):
        
        # Implement your custom user authentication logic here
        if username == "admin" and password == "admin":
            return User(role=UserRole.Admin)
        elif username == "user" and password == "user":
            return User(role=UserRole.User)
        else:
            return None

@dataclass
class Parameter:
    endpoint: str = ""
    server_name: str = ""
    namespace_uri: str = ""

    @classmethod
    def from_dict(cls, raw_param: dict | str) -> Parameter:
        try:
            if isinstance(raw_param, dict):
                param = cls()
                param.endpoint = f"opc.tcp://{str(raw_param['endpoint'])}"
                param.server_name = str(raw_param['server_name'])
                param.namespace_uri = str(raw_param['namespace_uri'])
                return param
            else:
                raise ValueError("Parameter must be a dictionary")
        except KeyError as e:
            raise PARAMETER_ERROR(f"Missing parameter: {e}")
        except Exception as e:
            raise PARAMETER_ERROR(f"Parameter parsing error: {e}")

@HiveComponentInfo(uuid='7e707be1-6270-4a26-b11b-08e578f9b3fa', name='OPCUA Server', inports=1, outports=0, error_types=ERROR_TYPES)
class HiveComponent(HiveComponentBase):
    def premain(self, param: dict | str) -> None:
        self.log.info(f"Parsing parameters: {param}")
        self.param = Parameter.from_dict(param)

        # サーバー証明書の作成と保存（現状は、固定の証明書を使う。）
        # current_file = Path(__file__)
        # config_path = current_file.parent
        # server_cert_dir = config_path / "server_certs"
        # key_path, cert_path = create_cert(server_cert_dir)
        # self.key_path = key_path
        # self.cert_path = cert_path
        current_file = Path(__file__)
        config_path = current_file.parent
        server_cert_dir = config_path / "server_certs"
        self.key_path = server_cert_dir / "server_key.pem"
        self.cert_path = server_cert_dir / "server_cert.pem"

        # クライアント証明書の信頼ストアのパスを設定（いずれparameterで受けとるようにする）
        self.trust_client_cert_store = Path("C:/Users/tteng/work/my-synapse-components/opcua-server/.synapse/var-speedbeesynapse/certs") / "trust_store"

    def main(self, _param: dict | str) -> None:
        asyncio.run(self._main())

    async def _main(self) -> None:
        user_manager = CustomUserManager(self.log)
        server = Server(user_manager=user_manager)
        await server.init()
        server.set_endpoint(self.param.endpoint)
        server.set_server_name(self.param.server_name)
        server.set_security_policy([
            ua.SecurityPolicyType.NoSecurity,
            ua.SecurityPolicyType.Basic128Rsa15_Sign,
            ua.SecurityPolicyType.Basic128Rsa15_SignAndEncrypt,
            ua.SecurityPolicyType.Basic256_Sign,
            ua.SecurityPolicyType.Basic256_SignAndEncrypt,
            ua.SecurityPolicyType.Basic256Sha256_Sign,
            ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt
        ])
        server.set_security_IDs(["Anonymous", "Username"])
        await server.load_certificate(self.cert_path)
        await server.load_private_key(self.key_path)
        await server.set_application_uri('urn:DESKTOP-394KAR9:Saltyster:SpeeDBeeSynapse')

        trust_store = TrustStore([self.trust_client_cert_store], [])
        await trust_store.load()
        validator = CertificateValidator(
            CertificateValidatorOptions.TRUSTED | CertificateValidatorOptions.PEER_CLIENT, trust_store
        )
        server.set_certificate_validator(validator)

        namespace_idx = await server.register_namespace(self.param.namespace_uri)
        self.opcua_components_folder = await OPCUAComponentsFolder.create(server, namespace_idx)

        async with server:
            while self.is_runnable():
                columns = self.in_port1.get_columns()
                for column in columns:
                    # source_nameに一致するコンポーネントを取得
                    component_obj = self.opcua_components_folder.get_component_object(column.source_name)
                    if component_obj is None:
                        component_obj = await self.opcua_components_folder.add_component_object(namespace_idx, column.source_name)
                        self.log.info(f"Added new component: {component_obj.name}")

                    # data_nameに一致する変数を取得
                    variable = component_obj.get_variable(column.data_name)
                    if variable is None:
                        variable = await component_obj.add_variable(namespace_idx, column)
                        self.log.info(f"Added new variable: {variable.name} to component: {component_obj.name}")

                    # 変数の値を更新
                    await variable.update_value(column.get_latest_value()[1])

                await asyncio.sleep(1)
