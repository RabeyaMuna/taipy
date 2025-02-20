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

    init(canvasDomElement: HTMLElement, canvasEditModeCanvas?: HTMLElement) {
        this.#canvas.init(canvasDomElement, canvasEditModeCanvas);
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
    ) {
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
            getStore().addElementAction({ action: ElementActionEnum.Add, id, payload: properties });
            getStore().addElement({
                type,
                id,
                properties,
                ...renderConfig,
            });
            return;
        }
        // modify element if existed
        getStore().addElementAction({ action: ElementActionEnum.Add, id, payload: properties });
        getStore().editElement(id, { ...renderConfig, properties });
    }

    modifyElement(id: string, elementProperties: Element["properties"]) {
        getStore().addElementAction({ action: ElementActionEnum.Modify, id, payload: elementProperties });
        getStore().editElement(id, elementProperties);
    }

    deleteElement(id: string) {
        getStore().addElementAction({ action: ElementActionEnum.Delete, id });
        getStore().deleteElement(id);
    }
}
