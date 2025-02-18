import { nanoid } from "nanoid";
import { TaipyApp } from "../app";
import { TaipyCanvas } from "./canvas";
import { ElementRenderer } from "./elementRenderer";
import useStore from "../store";

export interface Element {
    type: string;
    id?: string;
    properties?: Record<string, string>;
    wrapperHtml?: [string, string];
    wrapperHtmlEditMode?: [string, string];
    jsx?: string;
    editModeJsx?: string;
}

export class ElementManager {
    _elements: Element[];
    _renderer: ElementRenderer;
    _canvas: TaipyCanvas;
    taipyApp: TaipyApp;

    constructor(taipyApp: TaipyApp) {
        this.taipyApp = taipyApp;
        this._elements = [];
        this._renderer = new ElementRenderer(taipyApp);
        this._canvas = new TaipyCanvas(taipyApp);
    }

    init(canvasDomElement: HTMLElement, canvasEditModeCanvas?: HTMLElement) {
        this._canvas.init(canvasDomElement, canvasEditModeCanvas);
    }

    setEditMode(editMode: boolean) {
        console.log("Setting edit mode to", editMode);
        const currentEditMode = useStore.getState().editMode;
        if (currentEditMode === editMode) {
            return;
        }
        useStore.getState().setEditMode(editMode);
        // Reset view mode canvas if switched back to edit mode
        if (editMode) {
            this._canvas.resetCanvas(false);
        }
        // if in view mode -> render it because chalkit will not be rendering it
        if (!editMode) {
            this.render(true);
        }
    }

    render(force: boolean = false) {
        const { editMode } = useStore.getState();
        this._renderer.render(this._elements, editMode, force).then((jsx) => this._canvas.updateContent(jsx, editMode));
    }

    addElement(element: Element) {
        if (element.id === undefined) {
            element.id = nanoid(10);
        }
        // check if element already exists based on id
        if (this._elements.find((el) => el.id === element.id)) {
            return;
        }
        this._elements.push(element);
        this.render();
    }

    modifyElement(id: string, elementProperties: Record<string, string>) {
        this._elements = this._elements.map((el) => {
            if (el.id !== id) {
                return el;
            }
            const properties = { ...el.properties, ...elementProperties };
            return { ...el, properties, jsx: "", editModeJsx: "" };
        });
        this.render();
    }

    deleteElement(id: string) {
        this._elements = this._elements.filter((el) => el.id !== id);
        this.render();
    }
}
