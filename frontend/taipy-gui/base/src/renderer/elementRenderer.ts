import { TaipyApp } from "../app";
import { Element } from "./elementManager";
import axios from "axios";

export class ElementRenderer {
    taipyApp: TaipyApp;

    constructor(taipyApp: TaipyApp) {
        this.taipyApp = taipyApp;
    }

    async render(elements: Element[], editMode: boolean, force: boolean = false): Promise<string> {
        const renderedElements = await Promise.all(
            elements.map(async (element) => {
                const jsxMode = editMode ? "editModeJsx" : "jsx";
                const wrapperHtml = editMode ? element.wrapperHtmlEditMode : element.wrapperHtml;
                if (force || !element[jsxMode]) {
                    element[jsxMode] = await this.renderSingle(element, editMode);
                }
                return `${wrapperHtml?.[0] || ""}${element[jsxMode]}${wrapperHtml?.[1] || ""}`;
            }),
        );
        return renderedElements.join("\n");
    }

    async renderSingle(element: Element, editMode: boolean): Promise<string> {
        try {
            const id = element.id + "-el" + (editMode ? "" : "-active");
            const result = await axios.post<{ jsx: string }>(
                `${this.taipyApp.getBaseUrl()}taipy-element-jsx?client_id=${this.taipyApp.clientId}`,
                {
                    type: element.type,
                    properties: { ...element.properties, id, active: !editMode },
                    context: this.taipyApp.getContext(),
                },
            );
            return result.data.jsx;
        } catch (error) {
            throw new Error(`Failed to render element '${element.type} - ${element.id}': ${error}`);
        }
    }
}
