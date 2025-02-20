import { TaipyApp } from "../app";
import { createRoot, Root } from "react-dom/client";
import { getStore } from "../store";
import { createElement } from "react";
import TaipyRendered from "../components/Taipy/TaipyRendered";

export class TaipyCanvas {
    taipyApp: TaipyApp;
    #root?: Root;
    #canvasElement?: HTMLElement;

    constructor(taipyApp: TaipyApp) {
        this.taipyApp = taipyApp;
    }

    init(canvasElement: HTMLElement, canvasEditModeElement?: HTMLElement) {
        if (!canvasElement) {
            console.error("Root element not found!");
            return;
        }
        getStore().setApp(this.taipyApp);
        this.initCanvas(canvasElement, false);
        if (canvasEditModeElement) {
            this.initCanvas(canvasEditModeElement, true);
            getStore().setEditMode(true);
        }
    }

    initCanvas(canvasElement: HTMLElement, editMode: boolean) {
        const root = createRoot(canvasElement);
        root.render(createElement(TaipyRendered, { editMode }));
        if (!editMode) {
            this.#canvasElement = canvasElement;
            this.#root = root;
        }
    }

    // only used for view mode canvas
    resetMainCanvas() {
        if (this.#root && this.#canvasElement) {
            try {
                this.#root.unmount();
            } catch (error) {
                console.error("Error while unmounting root canvas", error);
            }
            // remove all elements from canvas
            while (this.#canvasElement?.firstChild) {
                this.#canvasElement.removeChild(this.#canvasElement.firstChild);
            }
            getStore().resetMainCanvas();
            this.#root = createRoot(this.#canvasElement);
            this.#root.render(createElement(TaipyRendered, { editMode: false }));
        }
    }
}
