from __future__ import annotations

import asyncio
import typing
from asyncua import ua, Server
from asyncua.common.node import Node
from datetime import UTC, datetime
from dataclasses import dataclass
from speedbeesynapse.component.base import DataType, HiveComponentBase, HiveComponentInfo, ErrorType


PARAMETER_ERROR = ErrorType('PARAMETER ERROR','detail')
ERROR_TYPES = [PARAMETER_ERROR]


class OPCUAVariable:
    def __init__(self, data_name: str, data_type: str, node: Node):
        self.name = data_name
        self.node = node
        self.data_type = data_type

    async def update_value(self, value: any):
        await self.node.write_value(value)

class OPCUAComponent:
    def __init__(self, component_name: str, node: Node):
        self.name: str = component_name
        self.node: Node = node
        self.variables: list[OPCUAVariable] = []

    def get_variable(self, variable_name: str) -> typing.Optional[OPCUAVariable]:
        for variable in self.variables:
            if variable.name == variable_name:
                return variable
        return None
    
    async def create_variable(self, column: any, name_space: int):
        variable_node = await self.node.add_variable(name_space, column.data_name, column.get_latest_value()[1])
        variable = OPCUAVariable(column.data_name, column.data_type, variable_node)
        self.variables.append(variable)
        return variable

class OPCUAComponentManager:
    def __init__(self):
        self.components: list[OPCUAComponent] = []

    def get_component(self, component_name: str) -> typing.Optional[OPCUAComponent]:
        for component in self.components:
            if component.name == component_name:
                return component
        return None

    async def create_component(self, component_name: str, name_space: int, folder: Node) -> OPCUAComponent:
        component_node = await folder.add_object(name_space, component_name)
        component = OPCUAComponent(component_name, component_node)
        self.components.append(component)
        return component

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
        self.opcua_component_manager: OPCUAComponentManager = OPCUAComponentManager()

    def main(self, _param: dict | str) -> None:
        asyncio.run(self._main())

    async def _main(self) -> None:
        server = Server()
        await server.init()
        server.set_endpoint(self.param.endpoint)
        server.set_server_name(self.param.server_name)
        server.set_security_policy([
            ua.SecurityPolicyType.NoSecurity,
            ua.SecurityPolicyType.Basic256Sha256_Sign,
            ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt
        ])

        idx = await server.register_namespace(self.param.namespace_uri)
        components_folder = await server.nodes.objects.add_folder(idx, "Components")

        async with server:
            while self.is_runnable():
                columns = self.in_port1.get_columns()
                for column in columns:
                    self.log.info(column.source_name)
                    # source_nameに一致するコンポーネントを取得
                    component = self.opcua_component_manager.get_component(column.source_name)
                    if component is None:
                        component = await self.opcua_component_manager.create_component(column.source_name, idx, components_folder)
                        self.log.info(f"Added new component: {column.source_name}")

                    # data_nameに一致する変数を取得
                    variable = component.get_variable(column.data_name)
                    if variable is None:
                        variable = await component.create_variable(column, idx)
                        self.log.info(f"Added new variable: {column.data_name} to component: {component.name}")

                    # 変数の値を更新
                    await variable.update_value(column.get_latest_value()[1])

                await asyncio.sleep(1)
