import { create } from "zustand";
import { TaipyApp } from "./app";

interface TaipyGuiBaseState {
    editMode: boolean;
    jsx: string;
    editModeJsx: string;
    module: string;
    app?: TaipyApp;
    setEditMode: (newEditMode: boolean) => void;
    setJsx: (newJsx: string) => void;
    setEditModeJsx: (newJsx: string) => void;
    setModule: (newModule: string) => void;
    setApp: (newApp: TaipyApp) => void;
}

const useStore = create<TaipyGuiBaseState>()((set) => ({
    editMode: false,
    jsx: "",
    editModeJsx: "",
    module: "",
    app: undefined,
    setEditMode: (newEditMode: boolean) => set(() => ({ editMode: newEditMode })),
    setJsx: (newJsx: string) => set(() => ({ jsx: newJsx })),
    setEditModeJsx: (newJsx: string) => set(() => ({ editModeJsx: newJsx })),
    setModule: (newModule: string) => set(() => ({ module: newModule })),
    setApp: (newApp: TaipyApp) => set(() => ({ app: newApp })),
}));

export default useStore;
