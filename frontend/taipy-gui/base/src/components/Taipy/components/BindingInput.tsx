import React, { useMemo } from "react";
import { TaipyElementInput } from "./TaipyPropertyHandler";
import useStore from "../../../store";
import Box from "@mui/material/Box";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import Select, { SelectChangeEvent } from "@mui/material/Select";

const common = (props: TaipyElementInput, bindingInfo: string[][]) => {
    const { onChange, value, defaultValue } = props;
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
        if (!app) {
            return [];
        }
        const varData = app.getDataTree();
        if (!varData) {
            return [];
        }
        const varDataModule = varData[app.getContext()];
        return Object.keys(varDataModule)
            .filter((key: string) => !key.includes("chlkt") && !key.toLowerCase().includes("taipy"))
            .map((key: string) => [varDataModule[key].encoded_name, key]);
    }, [app]);
    return common(props, data);
};

export const FunctionBindingInput = (props: TaipyElementInput) => {
    const app = useStore((state) => state.app);
    const data = useMemo(() => {
        if (!app) {
            return [];
        }
        return app
            .getFunctionList()
            .filter((key: string) => !key.includes("chlkt") && !key.toLowerCase().includes("taipy"))
            .map((key: string) => [key, key]);
    }, [app]);
    return common(props, data);
};
