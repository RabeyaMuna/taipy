import axios from "axios";
import { TaipyApp } from "../../app";
import { Element } from "../../element/elementManager";

export const getJsx = async (taipyApp: TaipyApp, element: Element, editMode: boolean): Promise<string> => {
    try {
        const id = element.id + "-el" + (editMode ? "" : "-active");
        const result = await axios.post<{ jsx: string }>(
            `${taipyApp.getBaseUrl()}taipy-element-jsx?client_id=${taipyApp.clientId}`,
            {
                type: element.type,
                properties: { ...element.properties, id },
                context: taipyApp.getContext(),
            },
        );
        return result.data.jsx;
    } catch (error) {
        throw new Error(`Failed to render element '${element.type} - ${element.id}': ${error}`);
    }
};
