import { TaipyApp } from "../app";
import { TaipyCanvas } from "./canvas";
import { getStore, isElementExisted } from "../store";

export interface CanvasRenderConfig {
    rootId: string;
    root: HTMLElement;
    wrapper: [string, string];
}

export interface Element {
    type: string;
    id: string;
    properties?: Record<string, unknown>;
    styles?: Record<string, unknown>;
    renderConfig?: CanvasRenderConfig;
    editModeRenderConfig?: CanvasRenderConfig;
}

export enum ElementActionEnum {
    Add = "add",
    Modify = "modify",
    Delete = "delete",
}

export interface ElementAction {
    action: ElementActionEnum;
    id: Element["id"];
    payload?: Record<string, unknown>;
    editMode?: boolean;
}

export class ElementManager {
    #canvas: TaipyCanvas;
    taipyApp: TaipyApp;

    constructor(taipyApp: TaipyApp) {
        this.taipyApp = taipyApp;
        this.#canvas = new TaipyCanvas(taipyApp);
    }

    init(
        canvasDomElement: HTMLElement,
        canvasEditModeCanvas?: HTMLElement,
        propertyEditorElement?: HTMLElement,
        styleHandler?: (id: string, styles: Record<string, unknown>) => void,
    ) {
        getStore().setStyleHandler(styleHandler);
        this.#canvas.init(canvasDomElement, canvasEditModeCanvas, propertyEditorElement);
    }

    setEditMode(editMode: boolean) {
        const currentEditMode = getStore().editMode;
        if (currentEditMode === editMode) {
            return;
        }
        getStore().setEditMode(editMode);
        // Reset view mode canvas if switched back to edit mode
        if (editMode) {
            this.#canvas.resetMainCanvas();
        }
    }

    addElement(
        type: string,
        id: string,
        rootId: string,
        wrapper: CanvasRenderConfig["wrapper"],
        properties: Element["properties"] | undefined = undefined,
        styles: Element["styles"] | undefined = undefined,
    ) {
        if (properties === undefined) {
            properties = {};
        }
        if (styles === undefined) {
            styles = {};
        }
        const root = document.getElementById(rootId);
        if (!root) {
            console.error(`Root element with id '${rootId}' not found!`);
            return;
        }
        const renderConfig = {
            [getStore().editMode ? "editModeRenderConfig" : "renderConfig"]: { rootId, root, wrapper },
        };
        // add element if not existed
        if (!isElementExisted(id)) {
            getStore().addElementAction({
                action: ElementActionEnum.Add,
                id,
                payload: { properties, styles },
            });
            getStore().addElement({
                type,
                id,
                properties,
                styles,
                ...renderConfig,
            });
            return;
        }
        // modify element if existed
        const editedProperties = {
            ...getStore().elements.find((element) => element.id === id)?.properties,
            ...properties,
        };
        const editedStyles = {
            ...getStore().elements.find((element) => element.id === id)?.styles,
            ...styles,
        };
        getStore().addElementAction({
            action: ElementActionEnum.Add,
            id,
            payload: { properties: editedProperties, styles: editedStyles },
        });
        getStore().editElement(id, { ...renderConfig, properties: editedProperties, styles: editedStyles });
    }

    modifyElement(id: string, elementProperties: Record<string, unknown>) {
        getStore().addElementAction({ action: ElementActionEnum.Modify, id, payload: elementProperties });
        getStore().editElement(id, elementProperties);
    }

    modifyElementProperties(id: string, payload: Record<string, unknown>) {
        const properties = { ...getStore().elements.find((element) => element.id === id)?.properties, ...payload };
        this.modifyElement(id, { properties });
    }

    deleteElement(id: string) {
        getStore().addElementAction({ action: ElementActionEnum.Delete, id });
        getStore().deleteElement(id);
    }

    openPropertyEditor(id: string) {
        getStore().setSelectedElement(getStore().elements.find((element) => element.id === id));
    }

    closePropertyEditor() {
        getStore().setSelectedElement(undefined);
    }
}
