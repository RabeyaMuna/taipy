import React, { useCallback } from "react";
import { TaipyElementInput } from "./TaipyPropertyHandler";
import { Box, TextField } from "@mui/material";

function stripQuotes(str: string | undefined): string | undefined {
    if (str === undefined) {
        return str;
    }
    if (str.startsWith(`"`)) {
        str = str.slice(1);
    }
    if (str.endsWith(`"`)) {
        str = str.slice(0, -1);
    }
    return str;
}
const StringInput = (props: TaipyElementInput) => {
    const { value, defaultValue, onChange } = props;
    const inputOnChange = useCallback(
        (event: React.ChangeEvent<HTMLInputElement>) => {
            onChange(event.target.value);
        },
        [onChange],
    );
    return (
        <Box>
            <TextField
                variant="outlined"
                value={value !== undefined ? value : stripQuotes(defaultValue as string | undefined)}
                onChange={inputOnChange}
            />
        </Box>
    );
};

export default StringInput;
