import React, { ComponentType, useContext, useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { ErrorBoundary } from "react-error-boundary";
import JsxParser from "react-jsx-parser";

import { PageContext, TaipyContext } from "../../../../src/context/taipyContext";
import { Element, ElementActionEnum } from "../../renderer/elementManager";
import useStore, { getElementAction } from "../../store";
import { getJsx } from "./utils";
import { emptyArray } from "../../../../src/utils";
import ErrorFallback from "../../../../src/utils/ErrorBoundary";
import { getRegisteredComponents } from "../../../../src/components/Taipy";
import { renderError, unregisteredRender } from "../../../../src/components/Taipy/Unregistered";
import "./taipyelements.css";

interface TaipyElementProps {
    editMode: boolean;
    element: Element;
}

const TaipyElement = (props: TaipyElementProps) => {
    const { state } = useContext(TaipyContext);
    const [module, setModule] = useState<string>("");
    const [jsx, setJsx] = useState<string>("");
    const app = useStore((state) => state.app);
    const prevElement = useRef(props.element);

    const renderConfig = useMemo(
        () => (props.editMode ? props.element.editModeRenderConfig : props.element.renderConfig),
        [props.element, props.editMode],
    );

    const pageState = useMemo(() => {
        return { jsx, module };
    }, [jsx, module]);

    useEffect(() => {
        app && setModule(app.getContext());
    }, [app]);

    useEffect(() => {
        const setJsxAsync = async () => {
            if (!app || !renderConfig) {
                setJsx("");
                return;
            }
            const res = await getJsx(app, props.element, props.editMode);
            setJsx(`${renderConfig.wrapper[0]}${res}${renderConfig.wrapper[1]}`);
        };
        setJsxAsync();
    }, [app, props.editMode, props.element, renderConfig]);

    useEffect(() => {
        if (prevElement.current === props.element) {
            // Initial render
            const potentialAction = { action: ElementActionEnum.Add, id: props.element.id, editMode: props.editMode };
            app && app.onCanvasReRenderEvent(props.editMode, getElementAction(potentialAction));
        } else {
            // Modify render
            const potentialAction = {
                action: ElementActionEnum.Modify,
                id: props.element.id,
                editMode: props.editMode,
            };
            app && app.onCanvasReRenderEvent(props.editMode, getElementAction(potentialAction));
        }
        prevElement.current = props.element;
        return () => {
            // ComponenetWillUnmount --> delete element
            const potentialAction = {
                action: ElementActionEnum.Delete,
                id: props.element.id,
                editMode: props.editMode,
            };
            app && app.onCanvasReRenderEvent(props.editMode, getElementAction(potentialAction));
        };
    }, [props.element, app, props.editMode]);

    return renderConfig ? (
        createPortal(
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
            </PageContext.Provider>,
            renderConfig.root,
        )
    ) : (
        <></>
    );
};

export default TaipyElement;
