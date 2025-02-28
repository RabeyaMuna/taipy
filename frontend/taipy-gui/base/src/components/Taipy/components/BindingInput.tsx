import React from "react";
import { TaipyElementInput } from "./TaipyPropertyHandler";
import { Box } from "@mui/material";

const common = (props: TaipyElementInput, bindingInfo: Record<string, string>) => {
    return <Box>Input</Box>;
};
export const BindingInput = (props: TaipyElementInput) => {
    return common(props, {});
};

export const FunctionBindingInput = (props: TaipyElementInput) => {
    return common(props, {});
};
