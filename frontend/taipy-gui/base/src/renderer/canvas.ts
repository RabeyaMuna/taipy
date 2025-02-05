import { TaipyApp } from "../app";
import { createRoot } from "react-dom/client";
import useStore from "../store";
import { createElement } from "react";
import TaipyRendered from "../components/Taipy/TaipyRendered";

export class TaipyCanvas {
    taipyApp: TaipyApp;

    constructor(taipyApp: TaipyApp) {
        this.taipyApp = taipyApp;
    }

    init(domElement: HTMLElement) {
        if (domElement) {
            const root = createRoot(domElement);
            root.render(createElement(TaipyRendered));
            useStore.getState().setApp(this.taipyApp);
            useStore.getState().setModule(this.taipyApp.getContext());
        } else {
            console.error("Root element not found!");
        }
    }

    updateContent(jsx: string) {
        useStore.getState().setJsx(jsx);
    }
}
