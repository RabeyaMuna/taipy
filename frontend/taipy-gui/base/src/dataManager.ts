export type ModuleData = Record<string, VarName>;

export type VarName = Record<string, VarData>;

export interface VarData {
    type: string;
    value: unknown;
    encoded_name: string;
    data_update: boolean;
}

type ColumnName = string;

export type RequestDataOptions = {
    columns?: Array<ColumnName>;
    pagekey?: string;
    alldata?: boolean;
    start?: number;
    end?: number;
    filters?: Array<{ col: ColumnName; value: string | boolean | number; action: string }>;
    aggregates?: Array<ColumnName>;
    applies?: { [key: ColumnName]: string };
    infinite?: boolean;
    reverse?: boolean;
    orderby?: ColumnName;
    sort?: "asc" | "desc";
    styles?: { [key: ColumnName]: string };
    tooltips?: { [key: ColumnName]: string };
    handlenan?: boolean;
    compare_datas?: string;
};

type RequestDataEntry = {
    options: RequestDataOptions;
    receivedData: unknown;
};

export const getRequestedDataKey = (payload?: unknown) =>
    (!!payload && typeof payload == "object" && "pagekey" in payload && (payload["pagekey"] as string)) || undefined;

// This class hold the information of variables and real-time value of variables
export class DataManager {
    // key: encoded name, value: real-time value
    #data: Record<string, unknown>;
    // Initial data fetched from taipy-gui backend
    #init_data: ModuleData;
    // key: encodedName -> dataEventKey -> requeste data
    #requested_data: Record<string, Record<string, RequestDataEntry>>;

    constructor(variableModuleData: ModuleData) {
        this.#data = {};
        this.#init_data = {};
        this.#requested_data = {};
        this.init(variableModuleData);
    }

    init(variableModuleData: ModuleData) {
        // Identify changes between the new and old data
        const changes: ModuleData = {};
        for (const context in this.#init_data) {
            if (!(context in variableModuleData)) {
                changes[context] = this.#init_data[context];
                continue;
            }
            for (const variable in this.#init_data[context]) {
                if (!(variable in variableModuleData[context])) {
                    if (!(context in changes)) {
                        changes[context] = {};
                    }
                    changes[context][variable] = this.#init_data[context][variable];
                }
            }
        }
        if (Object.keys(changes).length !== 0) {
            console.error("Unmatched data tree! Removed changes: ", changes);
        }
        // Reset the initial data
        this.#init_data = variableModuleData;
        this.#data = {};
        for (const context in this.#init_data) {
            for (const variable in this.#init_data[context]) {
                const vData = this.#init_data[context][variable];
                this.#data[vData["encoded_name"]] = vData.value;
            }
        }
        return changes;
    }

    getEncodedName(varName: string, module: string): string | undefined {
        if (module in this.#init_data && varName in this.#init_data[module]) {
            return this.#init_data[module][varName].encoded_name;
        }
        return undefined;
    }

    // return [name, moduleName]
    getName(encodedName: string): [string, string] | undefined {
        for (const context in this.#init_data) {
            for (const variable in this.#init_data[context]) {
                const vData = this.#init_data[context][variable];
                if (vData.encoded_name === encodedName) {
                    return [variable, context];
                }
            }
        }
        return undefined;
    }

    get(encodedName: string, dataEventKey?: string): unknown {
        // handle requested data
        if (dataEventKey) {
            if (!(encodedName in this.#requested_data)) {
                throw new Error(`Encoded name '${encodedName}' is not available in Taipy GUI`);
            }
            if (!(dataEventKey in this.#requested_data[encodedName])) {
                throw new Error(
                    `Event key '${dataEventKey}' is not available for encoded name '${encodedName}' in Taipy GUI`,
                );
            }
            return this.#requested_data[encodedName][dataEventKey].receivedData;
        }
        // handle normal data
        if (!(encodedName in this.#data)) {
            throw new Error(`${encodedName} is not available in Taipy GUI`);
        }
        return this.#data[encodedName];
    }

    addRequestDataOptions(encodedName: string, dataEventKey: string, options: RequestDataOptions) {
        if (!(encodedName in this.#requested_data)) {
            this.#requested_data[encodedName] = {};
        }
        // This would overrides object with the same key
        this.#requested_data[encodedName][dataEventKey] = { options: options, receivedData: undefined };
    }

    getInfo(encodedName: string): VarData | undefined {
        for (const context in this.#init_data) {
            for (const variable in this.#init_data[context]) {
                const vData = this.#init_data[context][variable];
                if (vData.encoded_name === encodedName) {
                    return { ...vData, value: this.#data[encodedName] };
                }
            }
        }
        return undefined;
    }

    getDataTree(): ModuleData {
        return this.#init_data;
    }

    getAllData(): Record<string, unknown> {
        return this.#data;
    }

    update(encodedName: string, value: unknown, dataEventKey?: string) {
        // handle requested data
        if (dataEventKey) {
            if (!(encodedName in this.#requested_data)) {
                throw new Error(`Encoded name '${encodedName}' is not available in Taipy GUI`);
            }
            if (!(dataEventKey in this.#requested_data[encodedName])) {
                throw new Error(
                    `Event key '${dataEventKey}' is not available for encoded name '${encodedName}' in Taipy GUI`,
                );
            }
            this.#requested_data[encodedName][dataEventKey].receivedData = value;
            return;
        }
        // handle normal data
        if (!(encodedName in this.#data)) {
            throw new Error(`${encodedName} is not available in Taipy Gui`);
        }
        this.#data[encodedName] = value;
    }

    deleteRequestedData(encodedName: string, dataEventKey: string) {
        if (encodedName in this.#requested_data && dataEventKey in this.#requested_data[encodedName]) {
            delete this.#requested_data[encodedName][dataEventKey];
        }
    }

    getRequestedData() {
        return this.#requested_data;
    }
}
