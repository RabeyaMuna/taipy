import React, { useCallback, useEffect, useMemo, useState } from "react";
import useStore from "../../store";
import VisElementParser, { VisElementDetails } from "../../element/VisElementParser";
import TaipyPropertyHandler from "./components/TaipyPropertyHandler";
import { Box, Button, createTheme, CssBaseline, ThemeProvider } from "@mui/material";

const darkTheme = createTheme({
    palette: {
        mode: "dark",
    },
});

const TaipyElementEditor = () => {
    // element from the selected item will not be updated since it is not a reference just a copy
    // -> need to use the elemnent from the main entry
    const elementId = useStore((state) => state.selectedElement?.id);
    const elements = useStore((state) => state.elements);
    const element = useMemo(() => elements.find((e) => e.id === elementId), [elementId, elements]);

    const app = useStore((state) => state.app);
    const [modifiedProperties, setModifiedProperties] = useState<Record<string, unknown>>({});
    const elementProperties = useMemo(() => element?.properties, [element?.properties]);
    const [availableProperties, propertyOrder] = useMemo(
        () =>
            element
                ? VisElementParser.getInstance().getDesignerProperty(element.type)
                : ([{}, []] as VisElementDetails),
        [element],
    );
    const defaultProperties = useMemo(
        () =>
            propertyOrder.reduce(
                (obj: Record<string, undefined>, k: string) => {
                    obj[k] = undefined;
                    return obj;
                },
                {} as Record<string, undefined>,
            ),
        [propertyOrder],
    );
    const actionButtonActiveStatus = useMemo(() => {
        // compare modified properties with element properties
        if (!elementProperties || !modifiedProperties) {
            return false;
        }
        const elementPropertiesFilled: Record<string, unknown> = { ...defaultProperties, ...elementProperties };
        if (modifiedProperties.length !== elementPropertiesFilled.length) {
            return false;
        }
        for (const key in modifiedProperties) {
            if (modifiedProperties[key] !== elementPropertiesFilled[key]) {
                return true;
            }
        }
        return false;
    }, [modifiedProperties, elementProperties, defaultProperties]);

    // USE_EFFECT
    // update property selection every time element property changes
    useEffect(() => {
        setModifiedProperties({ ...defaultProperties, ...elementProperties });
    }, [elementProperties, defaultProperties]);

    // CALLBACKS
    // update local selection
    const updateModifiedProperties = useCallback(
        (propertyName: string) => (value: unknown) => {
            setModifiedProperties((prev) => ({ ...prev, [propertyName]: value }));
        },
        [],
    );

    // push modification to main app
    const modifyElement = useCallback(() => {
        if (element) {
            // filter out undefined properties
            const filteredModifiedProperties = Object.keys(modifiedProperties).reduce(
                (obj: Record<string, unknown>, key) => {
                    if (modifiedProperties[key] !== undefined) {
                        obj[key] = modifiedProperties[key];
                    }
                    return obj;
                },
                {},
            );
            app?.modifyElement(element.id, { properties: filteredModifiedProperties });
        }
    }, [app, modifiedProperties, element]);

    // reset local selection
    const resetModifiedProperties = useCallback(() => {
        setModifiedProperties({ ...defaultProperties, ...elementProperties });
    }, [elementProperties, defaultProperties]);

    // RENDER
    return element ? (
        <ThemeProvider theme={darkTheme}>
            <CssBaseline />
            <Box>
                <h2>Properties for {element.type} widget</h2>
            </Box>
            <Box sx={{ my: 2 }}>
                {propertyOrder.map((propertyName) => (
                    <TaipyPropertyHandler
                        name={propertyName}
                        value={modifiedProperties[propertyName]}
                        defaultValue={availableProperties[propertyName].default_value}
                        onChange={updateModifiedProperties(propertyName)}
                        inputTypes={availableProperties[propertyName].designer_input_types}
                        description={availableProperties[propertyName].doc}
                        key={propertyName}
                    />
                ))}
            </Box>
            <Box display="flex" alignItems="center" justifyContent="center" sx={{ mt: 3 }}>
                <Button
                    onClick={resetModifiedProperties}
                    variant="contained"
                    color="warning"
                    disabled={!actionButtonActiveStatus}
                >
                    Reset
                </Button>
                <Button onClick={modifyElement} variant="contained" sx={{ ml: 3 }} disabled={!actionButtonActiveStatus}>
                    Save
                </Button>
            </Box>
        </ThemeProvider>
    ) : (
        <h2>No Taipy Element Selected</h2>
    );
};

export default TaipyElementEditor;
