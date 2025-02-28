import { Box, IconButton, Typography } from "@mui/material";
import React, { useCallback, useMemo, useState } from "react";
import Tooltip from "@mui/material/Tooltip";
import InfoIcon from "@mui/icons-material/Info";
import ChangeCircleIcon from "@mui/icons-material/ChangeCircle";
import parse from "html-react-parser";
import NumberInput from "./NumberInput";
import { BindingInput, FunctionBindingInput } from "./BindingInput";
import ExpressionInput from "./ExpressionInput";

interface TaipyPropertyHandlerProps {
    name: string;
    value: unknown;
    onChange: (value: unknown) => void;
    inputTypes: string[];
    description: string;
    defaultValue?: unknown;
}

export interface TaipyElementInput {
    value: TaipyPropertyHandlerProps["value"];
    defaultValue?: TaipyPropertyHandlerProps["defaultValue"];
    onChange: TaipyPropertyHandlerProps["onChange"];
}

const elementTypeComponentMap: Record<string, React.FC<TaipyElementInput>> = {
    number: NumberInput,
    binding: BindingInput,
    expression: ExpressionInput,
    functionbinding: FunctionBindingInput,
};

const inlineElementTypeComponenetMap: Record<string, React.FC<TaipyElementInput>> = {
    boolean: BindingInput,
};

const tooltipPropsSx = {
    tooltip: {
        sx: {
            fontSize: 12,
        },
    },
};

const TaipyPropertyHandler = (props: TaipyPropertyHandlerProps) => {
    const { name, value, onChange, inputTypes, description, defaultValue } = props;
    const [type, setType] = useState<string>(inputTypes[0]);
    const ElementTypeComponent = useMemo(() => elementTypeComponentMap[type], [type]);
    const InlineElementTypeComponent = useMemo(() => inlineElementTypeComponenetMap[type], [type]);

    const switchType = useCallback(() => {
        setType((prev) => {
            const index = inputTypes.indexOf(prev);
            return inputTypes[(index + 1) % inputTypes.length];
        });
    }, [inputTypes]);

    return (
        <>
            <Box display="flex" alignItems="center" sx={{ mt: 3, mb: 1 }}>
                <Typography fontSize={18} fontWeight={500}>
                    {name}
                </Typography>
                <Tooltip title={parse(description)} slotProps={tooltipPropsSx}>
                    <InfoIcon sx={{ ml: 0.5, fontSize: 12 }} />
                </Tooltip>
                {inputTypes.length > 1 ? (
                    <Tooltip title={"Switch to next input type"} slotProps={tooltipPropsSx}>
                        <IconButton onClick={switchType}>
                            <ChangeCircleIcon sx={{ ml: 1, fontSize: 20 }} />
                        </IconButton>
                    </Tooltip>
                ) : (
                    <></>
                )}
                {InlineElementTypeComponent ? (
                    <InlineElementTypeComponent value={value} defaultValue={defaultValue} onChange={onChange} />
                ) : (
                    <></>
                )}
            </Box>
            {ElementTypeComponent ? (
                <ElementTypeComponent value={value} defaultValue={defaultValue} onChange={onChange} />
            ) : (
                <></>
            )}
        </>
    );
};
export default TaipyPropertyHandler;
