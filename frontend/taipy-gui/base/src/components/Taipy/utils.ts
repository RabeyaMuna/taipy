import axios from "axios";
import { TaipyApp } from "../../app";
import { Element } from "../../element/elementManager";

export const getTaipyElementId = (id: Element["id"], editMode: boolean): string => {
    return id + "-el" + (editMode ? "" : "-active");
};

export const getJsx = async (taipyApp: TaipyApp, element: Element, editMode: boolean): Promise<string> => {
    try {
        const id = getTaipyElementId(element.id, editMode);
        const result = await axios.post<{ jsx: string }>(
            `${taipyApp.getBaseUrl()}taipy-element-jsx?client_id=${taipyApp.clientId}`,
            {
                type: element.type,
                properties: { id, ...element.properties },
                context: taipyApp.getContext(),
            },
        );
        return result.data.jsx;
    } catch (error) {
        throw new Error(`Failed to render element '${element.type} - ${element.id}': ${error}`);
    }
};

export const getVarList = (app?: TaipyApp) => {
    if (!app) {
        return [];
    }
    const varData = app.getDataTree();
    if (!varData) {
        return [];
    }
    const varDataModule = varData[app.getContext()];
    return Object.keys(varDataModule)
        .filter((key: string) => !key.includes("chlkt") && !key.toLowerCase().includes("taipy"))
        .map((key: string) => [key, key]);
    // .map((key: string) => [varDataModule[key].encoded_name, key]);
};

export const getFunctionList = (app?: TaipyApp) => {
    if (!app) {
        return [];
    }
    return app
        .getFunctionList()
        .filter((key: string) => !key.includes("chlkt") && !key.toLowerCase().includes("taipy"))
        .map((key: string) => [key, key]);
};
