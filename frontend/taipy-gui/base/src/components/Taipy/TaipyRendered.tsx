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

import React, { ComponentType, useEffect, useMemo, useReducer } from "react";
import { ErrorBoundary } from "react-error-boundary";
import JsxParser from "react-jsx-parser";

import { ThemeProvider } from "@mui/system";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFnsV3";

import { PageContext, TaipyContext } from "../../../../src/context/taipyContext";
import { emptyArray } from "../../../../src/utils";
import ErrorFallback from "../../../../src/utils/ErrorBoundary";
import { getRegisteredComponents } from "../../../../src/components/Taipy";
import { renderError, unregisteredRender } from "../../../../src/components/Taipy/Unregistered";
import {
    INITIAL_STATE,
    initializeWebSocket,
    taipyInitialize,
    taipyReducer,
} from "../../../../src/context/taipyReducers";
import useStore from "../../store";

interface TaipyRenderedProps {
    editMode?: boolean;
}

const TaipyRendered = (props: TaipyRenderedProps) => {
    const { editMode } = props;
    const jsx = useStore((state) => (editMode ? state.editModeJsx : state.jsx));
    const module = useStore((state) => state.module);
    const app = useStore((state) => state.app);
    const pageState = useMemo(() => {
        return { jsx, module };
    }, [jsx, module]);
    const [state, dispatch] = useReducer(taipyReducer, INITIAL_STATE, taipyInitialize);
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
        app && app.onCanvasReRenderEvent();
    }, [jsx, app]);

    return (
        <TaipyContext.Provider value={{ state, dispatch }}>
            <ThemeProvider theme={state.theme}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                    <PageContext.Provider value={pageState}>
                        <ErrorBoundary FallbackComponent={ErrorFallback}>
                            <JsxParser
                                disableKeyGeneration={true}
                                bindings={state.data}
                                components={getRegisteredComponents() as Record<string, ComponentType>}
                                jsx={pageState.jsx}
                                renderUnrecognized={unregisteredRender}
                                allowUnknownElements={false}
                                renderError={renderError}
                                blacklistedAttrs={emptyArray}
                                renderInWrapper={false}
                            />
                        </ErrorBoundary>
                    </PageContext.Provider>
                </LocalizationProvider>
            </ThemeProvider>
        </TaipyContext.Provider>
    );
};

export default TaipyRendered;
