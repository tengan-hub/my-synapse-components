export interface CustomUiApi {
  getComponentbases: () => Promise<any[]>;
  getPanels: () => Promise<any[]>;
  getPanel: (id: number) => Promise<any>;
  getComponents: (panelId?: number) => Promise<any[]>;
  getComponent: (id: string) => Promise<any>;
  getInPort: (id: string) => Promise<any>;
  getInPortData: (id: string) => Promise<any>;
  getInPortDataValue: (id: string) => Promise<any>;
  getSystemPort: (id: string) => Promise<any>;
  getSystemPortData: (id: string) => Promise<any>;
  getSystemPortDataValue: (id: string) => Promise<any>;
  getOutPort: (id: string) => Promise<any>;
  getOutPortData: (id: string) => Promise<any>;
  getOutPortDataValue: (id: string) => Promise<any>;
  runMethod: (id: string, methodName: string, parameter: any) => Promise<any>;
  getFlowlinks: (componentId?: string) => Promise<any[]>;
  getFlowlink: (id: string) => Promise<any>;
  getFlowlinkFilter: (id: string) => Promise<any>;
}
export interface CustomUiLib {
  onSave?: () => Promise<{}| null>;
  onLoad?: (editable: boolean, parameter: {}, new_component:  boolean, componentId?: string) => Promise<void>;
  api: CustomUiApi;
}
