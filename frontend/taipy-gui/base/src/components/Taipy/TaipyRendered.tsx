/*
 * Copyright 2021-2025 Avaiga Private Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 *
 *        http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

import React, { useEffect, useReducer } from "react";

import { ThemeProvider } from "@mui/system";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFnsV3";

import { TaipyContext } from "../../../../src/context/taipyContext";
import {
    createRefreshThemesAction,
    INITIAL_STATE,
    initializeWebSocket,
    taipyInitialize,
    taipyReducer,
} from "../../../../src/context/taipyReducers";
import useStore from "../../store";
import TaipyElement from "./TaipyElement";

interface TaipyRenderedProps {
    editMode: boolean;
}

const TaipyRendered = (props: TaipyRenderedProps) => {
    const [state, dispatch] = useReducer(taipyReducer, INITIAL_STATE, taipyInitialize);
    const elements = useStore((state) => state.elements);
    const themeClass = "taipy-" + state.theme.palette.mode;

    useEffect(() => {
        initializeWebSocket(state.socket, dispatch);
    }, [state.socket]);

    useEffect(() => {
        const classes = [themeClass];
        document.body.classList.forEach((cls) => {
            if (!cls.startsWith("taipy-")) {
                classes.push(cls);
            }
        });
        document.body.className = classes.join(" ");
    }, [themeClass]);

    useEffect(() => {
        const refreshThemes = () => {
            dispatch(createRefreshThemesAction());
        };
        window.addEventListener("refreshThemes", refreshThemes);
        return () => {
            window.removeEventListener("refreshThemes", refreshThemes);
        };
    }, []);

    return (
        <TaipyContext.Provider value={{ state, dispatch }}>
            <ThemeProvider theme={state.theme}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                    {elements.map((element) => (
                        <TaipyElement element={element} key={element.id} editMode={props.editMode} />
                    ))}
                </LocalizationProvider>
            </ThemeProvider>
        </TaipyContext.Provider>
    );
};

export default TaipyRendered;
