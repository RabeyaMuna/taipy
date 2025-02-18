import { TaipyApp } from "../app";
import { createRoot, Root } from "react-dom/client";
import useStore from "../store";
import { createElement } from "react";
import TaipyRendered from "../components/Taipy/TaipyRendered";

export class TaipyCanvas {
    taipyApp: TaipyApp;
    #root?: Root;
    #editModeRoot?: Root;
    #canvasElement?: HTMLElement;
    #canvasEditModeElement?: HTMLElement;

    constructor(taipyApp: TaipyApp) {
        this.taipyApp = taipyApp;
    }

    init(canvasElement: HTMLElement, canvasEditModeElement?: HTMLElement) {
        if (canvasElement) {
            this.initCanvas(canvasElement, false);
            useStore.getState().setApp(this.taipyApp);
            useStore.getState().setModule(this.taipyApp.getContext());
            if (canvasEditModeElement) {
                this.initCanvas(canvasEditModeElement, true);
                useStore.getState().setEditMode(true);
            }
        } else {
            console.error("Root element not found!");
        }
    }

    initCanvas(canvasElement: HTMLElement, editMode: boolean) {
        if (editMode) {
            this.#canvasEditModeElement = canvasElement;
            this.#editModeRoot = createRoot(this.#canvasEditModeElement);
            this.#editModeRoot.render(createElement(TaipyRendered, { editMode }));
            return;
        }
        this.#canvasElement = canvasElement;
        this.#root = createRoot(this.#canvasElement);
        this.#root.render(createElement(TaipyRendered, { editMode }));
    }

    resetCanvas(editMode: boolean) {
        if (editMode && this.#editModeRoot) {
            this.#editModeRoot.unmount();
            // remove all elements from canvas
            while (this.#canvasEditModeElement?.firstChild) {
                this.#canvasEditModeElement.removeChild(this.#canvasEditModeElement.firstChild);
            }
            useStore.getState().setEditModeJsx("");
            this.#editModeRoot.render(createElement(TaipyRendered, { editMode }));
            return;
        }
        if (!editMode && this.#root && this.#canvasElement) {
            // remove all elements from canvas
            try {
                this.#root.unmount();
            } catch (error) {
                console.error("Error while unmounting root canvas", error);
            }
            while (this.#canvasElement?.firstChild) {
                this.#canvasElement.removeChild(this.#canvasElement.firstChild);
            }
            useStore.getState().setJsx("");
            this.#root = createRoot(this.#canvasElement);
            this.#root.render(createElement(TaipyRendered, { editMode }));
        }
    }

    updateContent(jsx: string, editMode: boolean) {
        if (editMode) {
            useStore.getState().setEditModeJsx(jsx);
            return;
        }
        useStore.getState().setJsx(jsx);
    }
}
