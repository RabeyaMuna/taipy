import { create } from "zustand";
import { TaipyApp } from "./app";
import { Element, ElementAction } from "./element/elementManager";

interface TaipyGuiBaseState {
    editMode: boolean;
    app?: TaipyApp;
    elements: Element[];
    elementActions: ElementAction[];
    selectedElement?: Element;
    setEditMode: (newEditMode: boolean) => void;
    setApp: (newApp: TaipyApp) => void;
    addElement: (newElement: Element) => void;
    editElement: (id: string, payload: Record<string, unknown>) => void;
    resetMainCanvas: () => void;
    deleteElement: (id: string) => void;
    addElementAction: (action: ElementAction) => void;
    deleteElementAction: (action: ElementAction) => void;
    setSelectedElement: (action: Element | undefined) => void;
}

export const useStore = create<TaipyGuiBaseState>()((set) => ({
    editMode: false,
    app: undefined,
    elements: [],
    elementActions: [],
    selectedElement: undefined,
    setEditMode: (newEditMode: boolean) => set(() => ({ editMode: newEditMode })),
    setApp: (newApp: TaipyApp) => set(() => ({ app: newApp })),
    addElement: (newElement: Element) => set((state) => ({ elements: [...state.elements, newElement] })),
    editElement: (id: string, payload: Record<string, unknown>) =>
        set((state) => ({
            elements: state.elements.map((element) => (element.id === id ? { ...element, ...payload } : element)),
        })),
    deleteElement: (id: string) =>
        set((state) => ({ elements: state.elements.filter((element) => element.id !== id) })),
    resetMainCanvas: () =>
        set((state) => ({ elements: state.elements.map((el) => ({ ...el, renderConfig: undefined })) })),
    addElementAction: (action: ElementAction) =>
        set((state) => ({ elementActions: [...state.elementActions, { ...action, editMode: state.editMode }] })),
    deleteElementAction: (action: ElementAction) =>
        set((state) => ({ elementActions: state.elementActions.filter((a) => a !== action) })),
    setSelectedElement: (element: Element | undefined) => set(() => ({ selectedElement: element })),
}));

export const getStore = () => useStore.getState();

export const isElementExisted = (id: string) => getStore().elements.find((element) => element.id === id) !== undefined;

export const getElementAction = (elementAction: ElementAction) => {
    const action = getStore().elementActions.find(
        (a) => elementAction.id === a.id && elementAction.action === a.action && elementAction.editMode == a.editMode,
    );
    if (action) {
        getStore().deleteElementAction(action);
    }
    return action;
};

export default useStore;
