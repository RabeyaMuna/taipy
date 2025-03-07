import React, { useCallback, useMemo } from "react";
import { TaipyElementInput } from "./TaipyPropertyHandler";
import { Box, Checkbox } from "@mui/material";

const BooleanInput = (props: TaipyElementInput) => {
    const { value, defaultValue, onChange } = props;
    const defaultValueParsed = useMemo(
        () => (defaultValue === "True" ? true : defaultValue === "false" ? false : undefined),
        [defaultValue],
    );

    const checkboxOnChange = useCallback(
        (event: React.ChangeEvent<HTMLInputElement>) => {
            onChange(event.target.checked);
        },
        [onChange],
    );

    return (
        <Box sx={{ display: "inline-block" }}>
            <Checkbox
                checked={(value as boolean | undefined) ?? defaultValueParsed ?? false}
                onChange={checkboxOnChange}
            />
        </Box>
    );
};

export default BooleanInput;
