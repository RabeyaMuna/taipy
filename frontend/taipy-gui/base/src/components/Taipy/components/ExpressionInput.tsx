import React from "react";
import { TaipyElementInput } from "./TaipyPropertyHandler";
import { Box, TextField } from "@mui/material";

const ExpressionInput = (props: TaipyElementInput) => {
    const { value, defaultValue, onChange } = props;
    const inputOnChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        onChange(event.target.value);
    };
    return (
        <Box>
            <TextField variant="outlined" value={value !== undefined ? value : ""} onChange={inputOnChange} />
        </Box>
    );
};

export default ExpressionInput;
