import React, { useMemo } from "react";
import { TaipyElementInput } from "./TaipyPropertyHandler";
import useStore from "../../../store";
import Box from "@mui/material/Box";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import Select, { SelectChangeEvent } from "@mui/material/Select";
import { getFunctionList, getVarList } from "../utils";

const common = (props: TaipyElementInput, bindingInfo: string[][]) => {
    const { onChange, value } = props;
    const handleChange = (event: SelectChangeEvent) => {
        if (event.target.value === "") {
            onChange(undefined);
        } else {
            onChange(event.target.value as string);
        }
    };
    return (
        <Box sx={{ width: 200 }}>
            <FormControl fullWidth>
                <Select value={value !== undefined ? (value as string) : ("" as string)} onChange={handleChange}>
                    <MenuItem value="">None</MenuItem>
                    {bindingInfo.map((item) => (
                        <MenuItem key={item[0]} value={`{${item[0]}}`}>
                            {item[1]}
                        </MenuItem>
                    ))}
                </Select>
            </FormControl>
        </Box>
    );
};
export const BindingInput = (props: TaipyElementInput) => {
    const app = useStore((state) => state.app);
    const data = useMemo(() => {
        return getVarList(app);
    }, [app]);
    return common(props, data);
};

export const FunctionBindingInput = (props: TaipyElementInput) => {
    const app = useStore((state) => state.app);
    const data = useMemo(() => {
        return getFunctionList(app);
    }, [app]);
    return common(props, data);
};
