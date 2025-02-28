import React from "react";
import { TaipyElementInput } from "./TaipyPropertyHandler";
import { Box, TextField } from "@mui/material";

const NumberInput = (props: TaipyElementInput) => {
    const { value, defaultValue, onChange } = props;
    const inputOnChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        onChange(event.target.value);
    };
    return (
        <Box>
            <TextField
                type="number"
                variant="standard"
                value={value !== undefined ? value : defaultValue}
                onChange={inputOnChange}
                slotProps={{
                    input: {
                        disableUnderline: true,
                    },
                }}
            />
        </Box>
    );
};

export default NumberInput;
