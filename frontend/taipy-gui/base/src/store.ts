import { create } from "zustand";
import { TaipyApp } from "./app";

interface TaipyGuiBaseState {
    jsx: string;
    module: string;
    app?: TaipyApp;
    setJsx: (newJsx: string) => void;
    setModule: (newModule: string) => void;
    setApp: (newApp: TaipyApp) => void;
}

const useStore = create<TaipyGuiBaseState>()((set) => ({
    jsx: "",
    module: "",
    app: undefined,
    setJsx: (newJsx: string) => set(() => ({ jsx: newJsx })),
    setModule: (newModule: string) => set(() => ({ module: newModule })),
    setApp: (newApp: TaipyApp) => set(() => ({ app: newApp })),
}));

export default useStore;
